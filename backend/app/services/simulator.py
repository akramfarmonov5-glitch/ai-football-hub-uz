import asyncio
import logging
import time
from datetime import timedelta
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import utcnow
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.match import Match
from app.models.news import News
from app.services.ai_engine import get_ai_engine
from app.services.football_api import FootballAPIService
from app.services.notifier import notify_goals
from app.services.sportsdb import SportsDBService
from app.services.websocket import manager

# Har bir qadamda nechta o'yinga AI tahlili tayyorlanadi. Cheklov ataylab:
# aks holda bir vaqtda o'nlab AI so'rovi ketib, hisobni bo'shatib qo'yardi.
AI_PREVIEWS_PER_TICK = 2

# Yangiliklar bundan tez-tez yozilmaydi (AI so'rovlarini cheklash uchun)
NEWS_MIN_INTERVAL_HOURS = 3

logger = logging.getLogger(__name__)


def _match_update_payload(match) -> dict:
    """Shape a Match ORM object into the WebSocket 'match_update' event."""
    return {
        "event": "match_update",
        "match": {
            "id": match.id,
            "score_home": match.score_home,
            "score_away": match.score_away,
            "status": match.status,
            "minute": match.minute,
            "timeline": match.timeline,
            "stats": match.stats,
            "win_probability": match.win_probability,
        },
    }


async def broadcast_updates(db: AsyncSession, updated_matches: list) -> None:
    """Broadcast each updated match over WebSocket and generate post-match
    AI analysis for freshly finished games. Shared by the background loop
    and the manual /admin/simulate endpoint (single source of truth)."""
    ai_service = get_ai_engine()
    for match in updated_matches:
        await manager.broadcast(_match_update_payload(match))

        if match.status == "FT" and not match.ai_analysis:
            match.ai_analysis = await ai_service.generate_post_match_analysis(
                match.home_team_name,
                match.away_team_name,
                f"{match.score_home}-{match.score_away}",
                match.stats or {},
                match.timeline or [],
            )
            db.add(match)
            await db.commit()


async def generate_missing_previews(db: AsyncSession) -> None:
    """Yaqinda boshlanadigan o'yinlarga AI o'yinoldi tahlilini tayyorlaydi.

    Faqat tahlili yo'q va eng yaqin boshlanadigan bir nechta o'yin olinadi —
    shu sababli AI so'rovlari soni nazorat ostida qoladi.
    """
    result = await db.execute(
        select(Match)
        .where(Match.status == "NS", Match.ai_preview.is_(None))
        .order_by(Match.match_time.asc())
        .limit(AI_PREVIEWS_PER_TICK)
    )
    pending = list(result.scalars().all())
    if not pending:
        return

    ai_service = get_ai_engine()
    for match in pending:
        match.ai_preview = await ai_service.generate_match_preview(
            match.home_team_name, match.away_team_name, match.league_name
        )
        db.add(match)
    await db.commit()
    logger.info("%d ta o'yinga AI tahlili tayyorlandi", len(pending))


async def generate_match_report(db: AsyncSession) -> Optional[News]:
    """Yakunlangan o'yin haqida yangilik yozadi.

    Busiz "Qaynoq Xabarlar" bo'limi bir marta yozilgan maqola bilan qotib
    qolardi — sayt haftalar o'tib ham eski yangilikni ko'rsatib turardi.

    Takrorlanishning oldi shunday olinadi: faqat oxirgi yangilikdan **keyin**
    tugagan o'yin haqida yoziladi. Ya'ni bir o'yin haqida ikki marta maqola
    chiqmaydi va yangi o'yin bo'lmasa yangi maqola ham yozilmaydi.
    """
    latest_news_at = await db.scalar(select(func.max(News.created_at)))

    if latest_news_at and utcnow() - latest_news_at < timedelta(hours=NEWS_MIN_INTERVAL_HOURS):
        return None

    query = select(Match).where(Match.status == "FT")
    if latest_news_at:
        query = query.where(Match.match_time > latest_news_at)

    match = await db.scalar(query.order_by(Match.match_time.desc()).limit(1))
    if not match:
        return None

    topic = (
        f"{match.league_name}: {match.home_team_name} {match.score_home}-"
        f"{match.score_away} {match.away_team_name} o'yini yakunlandi"
    )
    article = await get_ai_engine().generate_news_article(topic)

    # Slug generatsiyasi va unikalligi news endpointidagi bilan bir xil bo'lsin
    from app.api.endpoints.news import slugify

    base_slug = slugify(article["title"])
    slug = base_slug
    counter = 1
    while await db.scalar(select(News.id).where(News.slug == slug)):
        slug = f"{base_slug}-{counter}"
        counter += 1

    tags = list(article.get("tags") or [])
    tags.append(f"match-{match.id}")

    news = News(
        title=article["title"],
        slug=slug,
        summary=article.get("summary"),
        content=article["content"],
        tags=tags,
        is_published=True,
    )
    db.add(news)
    await db.commit()
    logger.info("Yangi maqola yozildi: %s", news.title)
    return news


async def run_simulation_loop(interval_seconds: Optional[int] = None) -> None:
    """Fon vazifasi: jadvalni tirik holatda ushlab turadi.

    Ikki rejim:
      * API_FOOTBALL_KEY bor  — faqat haqiqiy ma'lumot, API_FOOTBALL_POLL_SECONDS
        oralig'ida so'raladi (bepul tarif kunlik limitiga sig'ishi uchun).
      * kalit yo'q            — to'liq simulyatsiya: o'yinlar boshlanadi,
        davom etadi, tugaydi va jadvalga yangilari qo'shiladi.
    """
    interval = interval_seconds or settings.SIMULATION_INTERVAL_SECONDS
    last_real_fetch: Optional[float] = None

    if settings.API_FOOTBALL_KEY:
        rejim, poll_seconds = "API-Football", settings.API_FOOTBALL_POLL_SECONDS
    elif settings.SPORTSDB_ENABLED and settings.sportsdb_league_ids:
        rejim, poll_seconds = "TheSportsDB", settings.SPORTSDB_POLL_SECONDS
    else:
        rejim, poll_seconds = "simulyatsiya", 0

    logger.info("Fon vazifasi ishga tushdi (qadam: %ds, manba: %s)", interval, rejim)

    while True:
        await asyncio.sleep(interval)
        async with AsyncSessionLocal() as db:
            try:
                service = FootballAPIService(db)
                sportsdb = SportsDBService(db)

                if service.has_api_key or sportsdb.enabled:
                    # Haqiqiy manba: so'rovlar oralig'iga rioya qilamiz
                    now = time.monotonic()
                    if last_real_fetch is not None and now - last_real_fetch < poll_seconds:
                        continue
                    last_real_fetch = now

                    if service.has_api_key:
                        updated_matches = await service.fetch_and_update_real_matches()
                    else:
                        updated_matches = await sportsdb.sync_matches()
                else:
                    updated_matches = await service.advance_matches(allow_real_fetch=False)

                if updated_matches:
                    await broadcast_updates(db, updated_matches)

                # Sevimli jamoasi gol urgan foydalanuvchilarga Telegram xabari
                if service.new_goals:
                    await notify_goals(db, service.new_goals)

                await generate_missing_previews(db)
                await generate_match_report(db)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Simulyatsiya siklida xato")

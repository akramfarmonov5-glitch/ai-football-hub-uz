"""Sevimli jamoa gol urganda Telegram xabarnomasi.

Nima uchun bu yerda, botda emas: gollar backend simulyatorida (yoki real API
yangilanishida) tug'iladi. Bot esa alohida jarayon — u gol sodir bo'lganini
bilmaydi. Shuning uchun xabar to'g'ridan-to'g'ri Telegram HTTP API orqali
yuboriladi; bot ishlayotgan bo'lishi ham shart emas.

Foydalanuvchi `favorite_team` ni bot orqali tanlaydi (`/setteam`).
"""

import asyncio
import logging
from typing import Any, Dict, List

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.match import Match
from app.models.user import User

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"

# Bir vaqtda yuboriladigan xabarlar soni — Telegram limitiga urilmaslik uchun
SEND_CONCURRENCY = 20


def _escape_markdown(text: str) -> str:
    """Jamoa nomida `_` yoki `*` bo'lsa Telegram formatlashi buzilmasin."""
    for char in ("_", "*", "[", "]", "`"):
        text = text.replace(char, f"\\{char}")
    return text


def build_goal_message(match: Match, event: Dict[str, Any]) -> str:
    scoring_team = (
        match.home_team_name if event.get("team") == "home" else match.away_team_name
    )
    return (
        f"⚽️ *GOL!*  {_escape_markdown(scoring_team)}\n\n"
        f"*{_escape_markdown(match.home_team_name)} {match.score_home} - "
        f"{match.score_away} {_escape_markdown(match.away_team_name)}*\n"
        f"🏆 {_escape_markdown(match.league_name)} | {event.get('time')}-daqiqa\n"
        f"👤 {_escape_markdown(str(event.get('detail', '')))}\n\n"
        f"[O'yinni kuzatish]({settings.PUBLIC_SITE_URL}/matches/{match.id})"
    )


async def _find_subscribers(db: AsyncSession, match: Match) -> List[User]:
    """Shu o'yindagi jamoalardan birini sevimli deb belgilagan foydalanuvchilar."""
    result = await db.execute(
        select(User).where(
            User.telegram_id.isnot(None),
            User.favorite_team.in_((match.home_team_name, match.away_team_name)),
        )
    )
    return list(result.scalars().all())


async def _send_message(client: httpx.AsyncClient, chat_id: str, text: str) -> bool:
    try:
        response = await client.post(
            f"/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
        )
        if response.status_code == 200:
            return True
        # 403 = foydalanuvchi botni bloklagan; bu kutilgan holat, xato emas
        logger.info(
            "Telegram xabari yuborilmadi (chat %s): HTTP %s", chat_id, response.status_code
        )
    except Exception as exc:
        logger.warning("Telegram xabarida xato (chat %s): %s", chat_id, exc)
    return False


async def notify_goal(
    db: AsyncSession, match: Match, event: Dict[str, Any]
) -> int:
    """Gol haqida obunachilarga xabar yuboradi. Yuborilgan xabarlar sonini qaytaradi."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return 0  # bot sozlanmagan — jimgina o'tkazib yuboramiz

    subscribers = await _find_subscribers(db, match)
    if not subscribers:
        return 0

    text = build_goal_message(match, event)
    semaphore = asyncio.Semaphore(SEND_CONCURRENCY)

    async with httpx.AsyncClient(base_url=TELEGRAM_API, timeout=10.0) as client:

        async def send(user: User) -> bool:
            async with semaphore:
                return await _send_message(client, user.telegram_id, text)

        results = await asyncio.gather(
            *(send(user) for user in subscribers), return_exceptions=True
        )

    sent = sum(1 for r in results if r is True)
    logger.info(
        "Gol xabarnomasi: %d/%d foydalanuvchiga yuborildi (%s)",
        sent,
        len(subscribers),
        match.home_team_name,
    )
    return sent


async def notify_goals(
    db: AsyncSession, goals: List[tuple[Match, Dict[str, Any]]]
) -> None:
    """Bir qadamda sodir bo'lgan barcha gollar bo'yicha xabar yuboradi."""
    for match, event in goals:
        try:
            await notify_goal(db, match, event)
        except Exception:
            # Xabarnoma nosozligi simulyatsiyani to'xtatmasligi kerak
            logger.exception("Gol xabarnomasida kutilmagan xato")


async def notify_news_item(news_title: str, news_summary: str, news_slug: str) -> bool:
    """Yangi AI yangilikni Telegram kanalga chop etadi."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHANNEL_ID:
        return False

    text = (
        f"📰 *{_escape_markdown(news_title)}*\n\n"
        f"{_escape_markdown(news_summary or '')}\n\n"
        f"🔗 [Batafsil o'qish]({settings.PUBLIC_SITE_URL}/news/{news_slug})"
    )

    async with httpx.AsyncClient(base_url=TELEGRAM_API, timeout=10.0) as client:
        success = await _send_message(client, settings.TELEGRAM_CHANNEL_ID, text)
        if success:
            logger.info("Yangi maqola Telegram kanalga yuborildi: %s", news_title)
        return success


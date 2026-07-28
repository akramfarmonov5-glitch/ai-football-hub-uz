import logging
from datetime import timedelta

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from sqlalchemy import select

from app.core.clock import utcnow
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.match import Match
from app.models.news import News
from bot.keyboards.menus import match_actions_keyboard

logger = logging.getLogger(__name__)
router = Router()

# O'zbekiston vaqti (UTC+5). Bazada vaqt naive UTC saqlanadi.
UZ_OFFSET = timedelta(hours=5)


def _local_time(value) -> str:
    """Bazadagi UTC vaqtni Toshkent vaqtiga o'giradi."""
    if value is None:
        return "—"
    return (value + UZ_OFFSET).strftime("%H:%M")


def _xg(match: Match) -> str:
    """xG ko'rsatkichi. Statistika hali yo'q bo'lsa ham xato bermaydi."""
    stats = match.stats or {}
    xg = stats.get("xG") or {}
    return f"{xg.get('home', 0)} - {xg.get('away', 0)}"


from app.core.translation import translate_league, translate_team


@router.message(F.text == "Live o'yinlar ⚽")
async def show_live_matches(message: types.Message):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Match).where(Match.status == "LIVE").order_by(Match.match_time.desc())
        )
        live_matches = list(result.scalars().all())

    if not live_matches:
        await message.answer("Ayni paytda jonli efirda o'yinlar yo'q 📭")
        return

    for m in live_matches:
        league = translate_league(m.league_name)
        home = translate_team(m.home_team_name)
        away = translate_team(m.away_team_name)
        text = (
            f"🏆 *{league}* | {m.minute}-daqiqa\n"
            f"⚔️ *{home} {m.score_home} - {m.score_away} {away}*\n"
            f"📈 xG: {_xg(m)}\n"
        )
        await message.answer(
            text,
            reply_markup=match_actions_keyboard(m.id),
            parse_mode=ParseMode.MARKDOWN,
        )


@router.message(F.text == "Bugungi o'yinlar 📅")
async def show_today_matches(message: types.Message):
    """Bugungi (Toshkent vaqti bo'yicha) o'yinlar jadvali."""
    now_local = utcnow() + UZ_OFFSET
    day_start_utc = now_local.replace(hour=0, minute=0, second=0, microsecond=0) - UZ_OFFSET
    day_end_utc = day_start_utc + timedelta(days=1)

    async with AsyncSessionLocal() as db:
        # Filtr bazada bajariladi — ilgari hamma o'yin yuklanib, Python
        # tomonida saralanardi.
        result = await db.execute(
            select(Match)
            .where(Match.match_time >= day_start_utc, Match.match_time < day_end_utc)
            .order_by(Match.match_time.asc())
            .limit(50)
        )
        todays = list(result.scalars().all())

    if not todays:
        await message.answer("Bugun o'yinlar rejalashtirilmagan 📅")
        return

    lines = ["📅 *Bugungi o'yinlar jadvali:*", ""]
    for m in todays:
        if m.status == "LIVE":
            status_text = f"Jonli 🔴 ({m.minute}-daqiqa)"
        elif m.status == "FT":
            status_text = "Tugadi 🏁"
        else:
            status_text = f"Boshlanish vaqti: {_local_time(m.match_time)}"

        lines.append(f"🏆 {translate_league(m.league_name)}")
        lines.append(f"⚽ {translate_team(m.home_team_name)} vs {translate_team(m.away_team_name)}")
        lines.append(f"📌 {status_text}")
        if m.status in ("LIVE", "FT"):
            lines.append(f"🔢 Hisob: {m.score_home} - {m.score_away}")
        lines.append("-------------------------")

    await message.answer("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


@router.message(F.text == "Yangiliklar 📰")
async def show_news(message: types.Message):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(News)
            .where(News.is_published == True)  # noqa: E712 — SQL solishtiruvi
            .order_by(News.created_at.desc())
            .limit(5)
        )
        news_list = list(result.scalars().all())

    if not news_list:
        await message.answer("Yangiliklar topilmadi 📰")
        return

    for n in news_list:
        text = (
            f"📰 *{n.title}*\n\n"
            f"{n.summary or ''}\n\n"
            f"🔗 [Batafsil o'qish]({settings.PUBLIC_SITE_URL}/news/{n.slug})"
        )
        await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@router.message(F.text == "AI Prognozlar 🔮")
async def show_ai_predictions(message: types.Message):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Match)
            .where(Match.status != "FT")
            .order_by(Match.match_time.asc())
            .limit(5)
        )
        upcoming = list(result.scalars().all())

    if not upcoming:
        await message.answer("Prognozlar uchun mos o'yinlar yo'q 🔮")
        return

    for m in upcoming:
        prob = m.win_probability or {"home": 33, "draw": 34, "away": 33}
        preview = m.ai_preview or "Tez orada tahlil tayyorlanadi."
        # Telegram xabari 4096 belgidan oshmasligi kerak
        if len(preview) > 700:
            preview = preview[:700].rsplit(" ", 1)[0] + "..."

        home = translate_team(m.home_team_name)
        away = translate_team(m.away_team_name)
        league = translate_league(m.league_name)

        text = (
            f"🔮 *AI Prognozi: {home} - {away}*\n"
            f"🏆 Liga: {league}\n\n"
            f"📊 G'alaba qozonish ehtimollari:\n"
            f"🏠 Mezbon ({home}): {prob.get('home', 0)}%\n"
            f"🤝 Durang: {prob.get('draw', 0)}%\n"
            f"✈️ Mehmon ({away}): {prob.get('away', 0)}%\n\n"
            f"ℹ️ _AI Tahlil:_ {preview}"
        )
        await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@router.callback_query(F.data.startswith("ai_analysis_"))
async def callback_ai_analysis(callback: types.CallbackQuery):
    match_id = _match_id_from(callback.data)
    if match_id is None:
        await callback.answer("Noto'g'ri so'rov")
        return

    async with AsyncSessionLocal() as db:
        match = await db.get(Match, match_id)

    if not match:
        await callback.answer("O'yin topilmadi")
        return

    analysis = match.ai_analysis or match.ai_preview or "Hozircha tahlillar tayyor emas."
    if len(analysis) > 3500:
        analysis = analysis[:3500].rsplit(" ", 1)[0] + "..."

    home = translate_team(match.home_team_name)
    away = translate_team(match.away_team_name)

    await callback.message.answer(
        f"🧠 *AI Tahlili ({home} vs {away}):*\n\n{analysis}",
        parse_mode=ParseMode.MARKDOWN,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ai_prob_"))
async def callback_ai_prob(callback: types.CallbackQuery):
    match_id = _match_id_from(callback.data)
    if match_id is None:
        await callback.answer("Noto'g'ri so'rov")
        return

    async with AsyncSessionLocal() as db:
        match = await db.get(Match, match_id)

    if not match:
        await callback.answer("O'yin topilmadi")
        return

    prob = match.win_probability or {"home": 33, "draw": 34, "away": 33}
    home = translate_team(match.home_team_name)
    away = translate_team(match.away_team_name)

    text = (
        f"📊 *G'alaba ehtimoli ({home} vs {away}):*\n\n"
        f"🏠 {home}: {prob.get('home', 0)}%\n"
        f"🤝 Durang: {prob.get('draw', 0)}%\n"
        f"✈️ {away}: {prob.get('away', 0)}%"
    )
    await callback.message.answer(text, parse_mode=ParseMode.MARKDOWN)
    await callback.answer()


def _match_id_from(data: str | None) -> int | None:
    """`ai_prob_2001` -> 2001. Buzuq callback ma'lumotida xato bermaydi."""
    if not data:
        return None
    try:
        return int(data.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        logger.warning("Callback ma'lumotini o'qib bo'lmadi: %s", data)
        return None

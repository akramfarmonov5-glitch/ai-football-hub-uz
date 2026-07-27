import logging

from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from sqlalchemy import distinct, select

from app.core.database import AsyncSessionLocal
from app.models.match import Match
from app.models.user import User

logger = logging.getLogger(__name__)
router = Router()


async def _known_team_names() -> list[str]:
    """Bazadagi jamoa nomlari — kiritilgan nomni tekshirish uchun."""
    async with AsyncSessionLocal() as db:
        home = await db.execute(select(distinct(Match.home_team_name)))
        away = await db.execute(select(distinct(Match.away_team_name)))
    return sorted({*home.scalars().all(), *away.scalars().all()})


@router.message(F.text == "Sozlamalar ⚙️")
async def show_settings(message: types.Message):
    telegram_id = str(message.from_user.id)

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.telegram_id == telegram_id))

    fav_team = user.favorite_team if user and user.favorite_team else "Tanlanmagan"
    notify_state = "yoqilgan ✅" if user and user.favorite_team else "o'chirilgan ❌"

    text = (
        f"⚙️ *Sozlamalar*\n\n"
        f"👤 Foydalanuvchi: @{message.from_user.username or message.from_user.full_name}\n"
        f"⭐ Sevimli jamoa: *{fav_team}*\n"
        f"🔔 Gol bildirishnomalari: {notify_state}\n\n"
        f"O'zgartirish uchun:\n"
        f"`/setteam Pakhtakor`\n"
        f"`/unsetteam` — bildirishnomani o'chirish\n"
        f"`/teams` — mavjud jamoalar ro'yxati"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("teams"))
async def list_teams(message: types.Message):
    teams = await _known_team_names()
    if not teams:
        await message.answer("Hozircha jamoalar ro'yxati bo'sh.")
        return
    await message.answer(
        "*Mavjud jamoalar:*\n\n" + "\n".join(f"• {t}" for t in teams),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(Command("setteam"))
async def set_favorite_team(message: types.Message):
    telegram_id = str(message.from_user.id)
    parts = (message.text or "").split(" ", 1)

    if len(parts) < 2 or not parts[1].strip():
        await message.answer(
            "Iltimos, jamoa nomini ham yozing. Masalan: `/setteam Nasaf`\n"
            "Mavjud jamoalar: /teams",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    team_name = parts[1].strip()

    # Kiritilgan nomni bazadagi jamoalar bilan solishtiramiz — xato yozilsa
    # bildirishnoma hech qachon kelmasdi va sababi tushunarsiz bo'lardi.
    known = await _known_team_names()
    matched = next((t for t in known if t.lower() == team_name.lower()), None)
    if not matched:
        suggestions = [t for t in known if team_name.lower() in t.lower()][:5]
        hint = (
            "\n\nEhtimol shulardan biri: " + ", ".join(suggestions)
            if suggestions
            else "\n\nTo'liq ro'yxat: /teams"
        )
        await message.answer(f"*{team_name}* jamoasi topilmadi.{hint}", parse_mode=ParseMode.MARKDOWN)
        return

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=message.from_user.username or message.from_user.full_name,
            )
            db.add(user)
        user.favorite_team = matched
        await db.commit()

    await message.answer(
        f"Saqlandi! Sevimli jamoangiz: *{matched}* 🌟\n"
        f"Endi bu jamoa gol urganda darhol xabar beramiz 🔔",
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(Command("unsetteam"))
async def unset_favorite_team(message: types.Message):
    telegram_id = str(message.from_user.id)

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user or not user.favorite_team:
            await message.answer("Sizda sevimli jamoa tanlanmagan.")
            return
        user.favorite_team = None
        await db.commit()

    await message.answer("Bildirishnomalar o'chirildi 🔕")

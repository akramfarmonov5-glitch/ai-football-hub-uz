import logging

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User
from bot.keyboards.menus import main_menu

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.full_name

    async with AsyncSessionLocal() as db:
        try:
            user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
            if not user:
                db.add(User(telegram_id=telegram_id, username=username))
                await db.commit()
                logger.info("Yangi foydalanuvchi: %s", telegram_id)
        except Exception:
            await db.rollback()
            logger.exception("Foydalanuvchini saqlashda xato")

    welcome_text = (
        f"Assalomu alaykum, {username}!\n\n"
        f"*AI Football Hub Uzbekistan* botiga xush kelibsiz!\n"
        f"Bu yerda siz jonli futbol natijalari, tezkor yangiliklar va AI ekspert "
        f"tahlillarini olishingiz mumkin.\n\n"
        f"💡 Sevimli jamoangizni tanlasangiz, u gol urganda darhol xabar beramiz:\n"
        f"`/setteam Pakhtakor`\n\n"
        f"Quyidagi tugmalardan birini tanlang 👇"
    )
    await message.answer(welcome_text, reply_markup=main_menu(), parse_mode=ParseMode.MARKDOWN)


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "*Yordam bo'limi:*\n\n"
        "⚽ *Live o'yinlar* — ayni damda jonli efirda o'tayotgan o'yinlar.\n"
        "📅 *Bugungi o'yinlar* — bugun bo'lib o'tadigan barcha bahslar.\n"
        "📰 *Yangiliklar* — eng so'nggi futbol yangiliklari.\n"
        "🔮 *AI Prognozlar* — sun'iy intellekt tahlili va g'alaba ehtimollari.\n"
        "⚙️ *Sozlamalar* — sevimli jamoa va bildirishnomalar.\n\n"
        "*Buyruqlar:*\n"
        "`/setteam <jamoa>` — sevimli jamoani tanlash (gol xabarnomasi yoqiladi)\n"
        "`/unsetteam` — bildirishnomalarni o'chirish"
    )
    await message.answer(help_text, reply_markup=main_menu(), parse_mode=ParseMode.MARKDOWN)

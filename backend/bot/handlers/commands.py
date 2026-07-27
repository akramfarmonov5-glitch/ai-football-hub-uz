from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from bot.keyboards.menus import main_menu
from app.core.database import SessionLocal
from app.models.user import User

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = str(message.from_user.id)
    username = message.from_user.username or message.from_user.full_name
    
    # Save user to DB
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            db.add(user)
            db.commit()
    except Exception as e:
        print(f"Error saving user in bot: {e}")
    finally:
        db.close()

    welcome_text = (
        f"Assalomu alaykum, {username}! \n\n"
        f"**AI Football Hub Uzbekistan** botiga xush kelibsiz! \n"
        f"Bu yerda siz jonli futbol natijalari, tezkor yangiliklar va AI ekspert tahlillarini olishingiz mumkin. \n\n"
        f"Quyidagi tugmalardan birini tanlang 👇"
    )
    await message.answer(welcome_text, reply_markup=main_menu())

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Yordam bo'limi:\n\n"
        "⚽ **Live o'yinlar** - Ayni damda jonli efirda o'tayotgan o'yinlar ro'yxati.\n"
        "📅 **Bugungi o'yinlar** - Bugun bo'lib o'tadigan barcha bahslar.\n"
        "📰 **Yangiliklar** - Eng so'nggi va qaynoq futbol yangiliklari.\n"
        "🔮 **AI Prognozlar** - Sun'iy intellekt tomonidan tahlil qilingan o'yinlar va g'alaba ehtimollari."
    )
    await message.answer(help_text, reply_markup=main_menu())

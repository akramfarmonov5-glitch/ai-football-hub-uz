from aiogram import Router, F, types
from app.core.database import SessionLocal
from app.models.user import User

router = Router()

@router.message(F.text == "Sozlamalar ⚙️")
async def show_settings(message: types.Message):
    telegram_id = str(message.from_user.id)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        fav_team = user.favorite_team if user and user.favorite_team else "Tanlanmagan"
        
        text = (
            f"⚙️ **Sozlamalar**\n\n"
            f"👤 Foydalanuvchi: @{message.from_user.username or message.from_user.full_name}\n"
            f"⭐ Sevimli jamoangiz: **{fav_team}**\n\n"
            f"Sevimli jamoangizni o'zgartirish uchun jamoa nomini yozing, masalan:\n"
            f"`/setteam Real Madrid` yoki `/setteam Navbahor`"
        )
        await message.answer(text, parse_mode="Markdown")
    finally:
        db.close()

@router.message(F.text.startswith("/setteam"))
async def set_favorite_team(message: types.Message):
    telegram_id = str(message.from_user.id)
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.answer("Iltimos, jamoa nomini ham yozing. Masalan: `/setteam Nasaf`", parse_mode="Markdown")
        return
        
    team_name = parts[1].strip()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.favorite_team = team_name
            db.add(user)
            db.commit()
            await message.answer(f"Muvaffaqiyatli saqlandi! Sevimli jamoangiz: **{team_name}** 🌟", parse_mode="Markdown")
        else:
             await message.answer("Siz ro'yxatdan o'tmagansiz. Botni faollashtirish uchun /start buyrug'ini bosing.")
    finally:
        db.close()

from aiogram import Router, F, types
from app.core.database import SessionLocal
from app.models.match import Match
from app.models.news import News
from bot.keyboards.menus import match_actions_keyboard
from datetime import datetime, timedelta

router = Router()

@router.message(F.text == "Live o'yinlar ⚽")
async def show_live_matches(message: types.Message):
    db = SessionLocal()
    try:
        live_matches = db.query(Match).filter(Match.status == "LIVE").all()
        if not live_matches:
            await message.answer("Ayni paytda jonli efirda o'yinlar yo'q 📭")
            return
        
        for m in live_matches:
            text = (
                f"🏆 **{m.league_name}** | {m.minute}-daqiqa\n"
                f"⚔️ **{m.home_team_name} {m.score_home} - {m.score_away} {m.away_team_name}**\n"
                f"📈 xG: {m.stats.get('xG', {}).get('home', 0)} - {m.stats.get('xG', {}).get('away', 0) if m.stats else 0}\n"
            )
            await message.answer(text, reply_markup=match_actions_keyboard(m.id))
    finally:
        db.close()

@router.message(F.text == "Bugungi o'yinlar 📅")
async def show_today_matches(message: types.Message):
    db = SessionLocal()
    try:
        # Today's matches (we'll fetch matches starting today/NS)
        today = datetime.utcnow().date()
        matches = db.query(Match).all()
        
        filtered = [m for m in matches if m.match_time.date() == today]
        if not filtered:
             await message.answer("Bugun o'yinlar rejalashtirilmagan 📅")
             return

        text = "📅 **Bugungi o'yinlar jadvali:**\n\n"
        for m in filtered:
            time_str = (m.match_time + timedelta(hours=5)).strftime("%H:%M") # Local time UZT
            status_text = "Jonli 🔴" if m.status == "LIVE" else "Tugadi 🏁" if m.status == "FT" else f"Boshlanish vaqti: {time_str}"
            text += f"🏆 {m.league_name}\n⚽ {m.home_team_name} vs {m.away_team_name}\n📌 Status: {status_text}\n"
            if m.status in ["LIVE", "FT"]:
                text += f"🔢 Hisob: {m.score_home} - {m.score_away}\n"
            text += "-------------------------\n"
            
        await message.answer(text)
    finally:
        db.close()

@router.message(F.text == "Yangiliklar 📰")
async def show_news(message: types.Message):
    db = SessionLocal()
    try:
        news_list = db.query(News).filter(News.is_published == True).order_by(News.created_at.desc()).limit(5).all()
        if not news_list:
            await message.answer("Yangiliklar topilmadi 📰")
            return
        
        for n in news_list:
            text = (
                f"📰 **{n.title}**\n\n"
                f"{n.summary or ''}\n\n"
                f"🔗 [Batafsil o'qish](http://localhost:3000/news/{n.slug})"
            )
            await message.answer(text, parse_mode="Markdown")
    finally:
        db.close()

@router.message(F.text == "AI Prognozlar 🔮")
async def show_ai_predictions(message: types.Message):
    db = SessionLocal()
    try:
        # Show matches that are not started (NS) or LIVE
        upcoming = db.query(Match).filter(Match.status != "FT").all()
        if not upcoming:
            await message.answer("Prognozlar uchun mos o'yinlar yo'q 🔮")
            return
        
        for m in upcoming:
            prob = m.win_probability or {"home": 33, "draw": 34, "away": 33}
            text = (
                f"🔮 **AI Prognozi: {m.home_team_name} - {m.away_team_name}**\n"
                f"🏆 Liga: {m.league_name}\n\n"
                f"📊 G'alaba qozonish ehtimollari:\n"
                f"🏠 Mezbon: {prob.get('home') or 0}%\n"
                f"🤝 Durang: {prob.get('draw') or 0}%\n"
                f"✈️ Mehmon: {prob.get('away') or 0}%\n\n"
                f"ℹ️ *AI Tahlil:* {m.ai_preview or 'Tez orada tahlil tayyorlanadi.'}"
            )
            await message.answer(text, parse_mode="Markdown")
    finally:
        db.close()

@router.callback_query(F.data.startswith("ai_analysis_"))
async def callback_ai_analysis(callback: types.CallbackQuery):
    match_id = int(callback.data.split("_")[2])
    db = SessionLocal()
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            await callback.answer("O'yin topilmadi")
            return
        
        analysis = match.ai_analysis or match.ai_preview or "Hozircha tahlillar tayyor emas."
        await callback.message.answer(f"🧠 **AI Tahlili ({match.home_team_name} vs {match.away_team_name}):**\n\n{analysis}")
        await callback.answer()
    finally:
        db.close()

@router.callback_query(F.data.startswith("ai_prob_"))
async def callback_ai_prob(callback: types.CallbackQuery):
    match_id = int(callback.data.split("_")[2])
    db = SessionLocal()
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            await callback.answer("O'yin topilmadi")
            return
        
        prob = match.win_probability or {"home": 33, "draw": 34, "away": 33}
        text = (
            f"📊 **G'alaba ehtimoli tahlili ({match.home_team_name} vs {match.away_team_name}):**\n\n"
            f"🏠 Mezbon ({match.home_team_name}): {prob.get('home') or 0}%\n"
            f"🤝 Durang: {prob.get('draw') or 0}%\n"
            f"✈️ Mehmon ({match.away_team_name}): {prob.get('away') or 0}%"
        )
        await callback.message.answer(text)
        await callback.answer()
    finally:
        db.close()

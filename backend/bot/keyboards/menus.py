from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Live o'yinlar ⚽"),
                KeyboardButton(text="Bugungi o'yinlar 📅")
            ],
            [
                KeyboardButton(text="Yangiliklar 📰"),
                KeyboardButton(text="AI Prognozlar 🔮")
            ],
            [
                KeyboardButton(text="Sozlamalar ⚙️")
            ]
        ],
        resize_keyboard=True
    )

def match_actions_keyboard(match_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="AI Izoh va Tahlil 🧠", callback_data=f"ai_analysis_{match_id}"),
                InlineKeyboardButton(text="G'alaba ehtimoli 📊", callback_data=f"ai_prob_{match_id}")
            ]
        ]
    )

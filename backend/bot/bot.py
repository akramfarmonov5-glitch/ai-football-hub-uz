import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from app.core.config import settings
from bot.handlers import commands, matches, settings as settings_handler

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN env variable is missing! Bot cannot start.")
        print("Please define TELEGRAM_BOT_TOKEN in backend/.env or your environment variables.")
        return

    bot = Bot(token=token)
    dp = Dispatcher()

    # Register routers
    dp.include_router(commands.router)
    dp.include_router(matches.router)
    dp.include_router(settings_handler.router)

    logging.info("Starting Telegram Bot...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot polling error: {e}")

if __name__ == "__main__":
    # If run directly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")

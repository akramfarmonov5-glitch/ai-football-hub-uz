import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Football Hub Uzbekistan"
    DATABASE_URL: str = "sqlite:///./futbol.db"

    # AI Config
    GEMINI_API_KEY: str = ""

    # Telegram Bot Config
    TELEGRAM_BOT_TOKEN: str = ""

    # Secret for admin authentication
    SECRET_KEY: str = "supersecretkeyforuzfootballhub"

    # Token required in the X-Admin-Token header to call /admin/* endpoints
    ADMIN_TOKEN: str = "admin123"

    # Front-end origins allowed by CORS (comma-separated in .env)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # External APIs (Optional, we will use our mock engine if empty or failed)
    API_FOOTBALL_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

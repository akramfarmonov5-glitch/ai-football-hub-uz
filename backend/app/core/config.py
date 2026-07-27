from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ katalogi. Nisbiy yo'llar shunga nisbatan hisoblanadi, shuning uchun
# serverni qayerdan ishga tushirishdan qat'i nazar bir xil fayllar ishlatiladi.
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "AI Football Hub Uzbekistan"

    # Bo'sh qoldirilsa — backend/futbol.db (absolyut yo'l) ishlatiladi.
    DATABASE_URL: str = ""

    # --- AI ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- Telegram bot ---
    TELEGRAM_BOT_TOKEN: str = ""
    # Botdagi havolalar shu manzilga ishora qiladi
    PUBLIC_SITE_URL: str = "http://localhost:3000"

    # --- Xavfsizlik ---
    # Standart qiymat ataylab yo'q: sozlanmagan bo'lsa himoyalangan endpointlar
    # umuman ishlamaydi (fail-closed), tasodifan ochiq qolib ketmaydi.
    ADMIN_TOKEN: str = ""
    SECRET_KEY: str = ""

    # Front-end origins allowed by CORS (comma-separated in .env)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # --- Tashqi futbol API (ixtiyoriy; bo'sh bo'lsa simulyatsiya ishlaydi) ---
    API_FOOTBALL_KEY: str = ""
    API_FOOTBALL_LEAGUES: str = "39,140"

    @property
    def database_url(self) -> str:
        """Ishlatiladigan baza URL'i — SQLite uchun har doim absolyut yo'l.

        `sqlite:///./futbol.db` kabi nisbiy yo'l joriy katalogga bog'liq bo'lib,
        serverni boshqa joydan ishga tushirsangiz yangi bo'sh baza yaratilardi.
        """
        url = self.DATABASE_URL.strip()
        if not url:
            return f"sqlite:///{(BACKEND_DIR / 'futbol.db').as_posix()}"
        if url.startswith("sqlite:///./"):
            relative = url[len("sqlite:///./") :]
            return f"sqlite:///{(BACKEND_DIR / relative).as_posix()}"
        return url

    @property
    def api_football_league_ids(self) -> List[int]:
        """API_FOOTBALL_LEAGUES ("39,140") -> [39, 140]."""
        return [
            int(part.strip())
            for part in self.API_FOOTBALL_LEAGUES.split(",")
            if part.strip().isdigit()
        ]


settings = Settings()

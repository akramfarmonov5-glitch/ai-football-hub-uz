import os
from pathlib import Path
from typing import List, Optional

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

    # --- AI: asosiy yo'l (Gemini API kaliti) ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- AI: zaxira yo'l (Vertex AI + service account) ---
    # Asosiy kalit ishlamay qolsa shu yo'ldan urinib ko'riladi. Ikkalasi ham
    # ishlamasa AI matnlari o'zbekcha shablonlarga tushadi.
    GCP_PROJECT_ID: str = ""
    # Foydalanuvchilarda `VERTEX_PROJECT` nomi ham uchraydi — ikkalasi ham qabul qilinadi
    VERTEX_PROJECT: str = ""
    # `global` yangi Gemini modellari uchun ishlaydi; eskiroq modellar
    # ba'zan faqat aniq regionda (masalan us-central1) mavjud bo'ladi.
    VERTEX_LOCATION: str = "global"
    # Service account JSON fayli (backend/ ga nisbatan yoki absolyut yo'l).
    # Bo'sh bo'lsa GOOGLE_APPLICATION_CREDENTIALS, undan keyin ADC ishlatiladi.
    VERTEX_CREDENTIALS_FILE: str = ""
    # Vertex'dagi model nomi Gemini API'dagidan farq qilishi mumkin.
    # Bo'sh bo'lsa GEMINI_MODEL ishlatiladi.
    VERTEX_MODEL: str = ""

    # --- Telegram bot ---
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHANNEL_ID: str = ""
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

    # --- TheSportsDB: haqiqiy ma'lumotning asosiy manbai ---
    # Bepul kalitida O'zbekiston Superligasi bor. "3" — ochiq sinov kaliti;
    # o'z bepul kalitingizni olish tavsiya etiladi (thesportsdb.com).
    # Cheklov: bepul tarifda jonli daqiqama-daqiqa hisob yo'q, faqat
    # boshlanmagan (NS) va tugagan (FT) o'yinlar.
    SPORTSDB_ENABLED: bool = True
    SPORTSDB_API_KEY: str = "3"
    # 4794=O'zbekiston Superligasi   4480=UEFA Chempionlar ligasi
    # Yevropa "katta beshligi": 4328=Angliya  4335=Ispaniya  4332=Italiya
    #                           4331=Germaniya  4334=Fransiya
    # 4339=Turkiya Super Ligasi
    # Diqqat: ikkinchi divizionlar bilan adashtirmang —
    #   4676="Turkish 1 Lig"  4394="Serie B"  4399="2. Bundesliga"  4401="Ligue 2"
    SPORTSDB_LEAGUES: str = "4794,4480,4328,4335,4332,4331,4334,4339"
    SPORTSDB_POLL_SECONDS: int = 600
    # So'rovlar orasidagi tanaffus. Bepul tarif daqiqasiga 30 ta so'rov beradi;
    # har liga alohida so'raladi, shuning uchun tezlikni o'zimiz cheklaymiz.
    SPORTSDB_REQUEST_INTERVAL_MS: int = 2200

    # --- API-Football (ixtiyoriy, pullik; qo'yilsa TheSportsDB o'rniga ishlaydi) ---
    API_FOOTBALL_KEY: str = ""
    API_FOOTBALL_LEAGUES: str = "39,140"
    # API-Football bepul tarifi kuniga 100 so'rov beradi. 900 soniya (15 daqiqa)
    # = kuniga ~96 so'rov, ya'ni limitga sig'adi. Pullik tarifda kamaytiring.
    API_FOOTBALL_POLL_SECONDS: int = 900

    # Simulyator qadamlari orasidagi vaqt (o'yin daqiqasi shuncha vaqtda o'tadi)
    SIMULATION_INTERVAL_SECONDS: int = 10

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
    def vertex_project(self) -> str:
        """GCP loyiha ID'si — ikkala nomdan qaysi biri to'ldirilgan bo'lsa."""
        return (self.GCP_PROJECT_ID or self.VERTEX_PROJECT).strip()

    @property
    def vertex_model(self) -> str:
        return (self.VERTEX_MODEL or self.GEMINI_MODEL).strip()

    @property
    def vertex_credentials_path(self) -> Optional[Path]:
        """Service account fayliga absolyut yo'l (mavjud bo'lsa)."""
        raw = self.VERTEX_CREDENTIALS_FILE.strip() or os.environ.get(
            "GOOGLE_APPLICATION_CREDENTIALS", ""
        )
        if not raw:
            return None

        path = Path(raw)
        if not path.is_absolute():
            path = BACKEND_DIR / path
        return path if path.is_file() else None

    @property
    def sportsdb_league_ids(self) -> List[int]:
        return [
            int(part.strip())
            for part in self.SPORTSDB_LEAGUES.split(",")
            if part.strip().isdigit()
        ]

    @property
    def uses_real_data(self) -> bool:
        """Saytda haqiqiy o'yin ma'lumotlari ko'rsatiladimi?"""
        return bool(self.API_FOOTBALL_KEY) or (
            self.SPORTSDB_ENABLED and bool(self.sportsdb_league_ids)
        )

    @property
    def api_football_league_ids(self) -> List[int]:
        """API_FOOTBALL_LEAGUES ("39,140") -> [39, 140]."""
        return [
            int(part.strip())
            for part in self.API_FOOTBALL_LEAGUES.split(",")
            if part.strip().isdigit()
        ]


settings = Settings()

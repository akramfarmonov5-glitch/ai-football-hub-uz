"""Testlar uchun umumiy sozlamalar.

Har bir test moduli vaqtinchalik SQLite bazasida ishlaydi — loyiha bazasiga
umuman tegilmaydi.
"""

import os
import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Config o'qilishidan OLDIN muhitni tayyorlaymiz, aks holda haqiqiy .env
# qiymatlari (jumladan API kalitlari) ishlatilib ketardi.
_TEST_DB = Path(tempfile.mkdtemp(prefix="futbol-test-")) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"
os.environ["API_FOOTBALL_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["ADMIN_TOKEN"] = "test-admin-token"
# AI zaxira yo'li ham o'chiriladi — busiz testlar haqiqiy Vertex AI ga
# so'rov yuborishi mumkin edi (.env dagi loyiha ID va service account bilan).
os.environ["GCP_PROJECT_ID"] = ""
os.environ["VERTEX_PROJECT"] = ""
os.environ["VERTEX_CREDENTIALS_FILE"] = ""
# TheSportsDB ham o'chiriladi — testlar tarmoqqa umuman chiqmasligi kerak
os.environ["SPORTSDB_ENABLED"] = "false"

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402

from app.core.database import Base, async_engine, AsyncSessionLocal  # noqa: E402
import app.models  # noqa: F401,E402  — modellar Base'ga ro'yxatdan o'tishi uchun


TEST_ADMIN_TOKEN = "test-admin-token"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def db():
    """Har bir test uchun toza baza."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

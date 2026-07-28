"""Baza ulanishlari: sinxron (bot, migratsiyalar) va asinxron (API).

SQLite ham, PostgreSQL (Neon) ham qo'llab-quvvatlanadi — `DATABASE_URL`
qiymatiga qarab aniqlanadi.
"""

from typing import Any, Dict, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Shared declarative base for all models
Base = declarative_base()

# Neon va boshqa hostinglar ulanish satriga qo'shadigan, lekin `asyncpg`
# tushunmaydigan parametrlar. Ular olib tashlanib, SSL alohida beriladi.
_PSYCOPG_ONLY_PARAMS = {"sslmode", "channel_binding", "options", "target_session_attrs"}


def _normalize_scheme(url: str) -> str:
    """`postgres://` -> `postgresql://` (ba'zi hostinglar eski shaklni beradi)."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _split_async_url(url: str) -> Tuple[str, Dict[str, Any]]:
    """Asinxron drayver uchun URL va `connect_args` juftligini qaytaradi.

    `asyncpg` `sslmode` kabi parametrlarni qabul qilmaydi — ular URL'dan
    olib tashlanadi va o'rniga `ssl=True` beriladi. Busiz Neon'ga ulanish
    "connect() got an unexpected keyword argument 'sslmode'" bilan yiqilardi.
    """
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1), {}

    if not url.startswith("postgresql://"):
        return url, {}

    parts = urlsplit(url)
    params = dict(parse_qsl(parts.query))

    ssl_kerak = params.get("sslmode", "").lower() not in ("", "disable", "allow")
    qolgan = {k: v for k, v in params.items() if k not in _PSYCOPG_ONLY_PARAMS}

    async_url = urlunsplit(
        (
            "postgresql+asyncpg",
            parts.netloc,
            parts.path,
            urlencode(qolgan),
            parts.fragment,
        )
    )
    return async_url, ({"ssl": True} if ssl_kerak else {})


DATABASE_URL = _normalize_scheme(settings.database_url)
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# ---------------------------------------------------------------------------
# Sync engine — Telegram bot va Alembic migratsiyalari uchun.
# ---------------------------------------------------------------------------
_sync_connect_args: Dict[str, Any] = (
    {"check_same_thread": False} if IS_SQLITE else {}
)

# `pool_pre_ping` — Neon bo'sh turgan ulanishni yopadi; busiz birinchi
# so'rov "server closed the connection unexpectedly" bilan yiqilardi.
_sync_kwargs: Dict[str, Any] = {"connect_args": _sync_connect_args}
if not IS_SQLITE:
    _sync_kwargs.update(pool_pre_ping=True, pool_recycle=300)

engine = create_engine(DATABASE_URL, **_sync_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Sync DB session dependency (bot / legacy use)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Async engine — FastAPI endpointlari va fon vazifasi uchun.
# ---------------------------------------------------------------------------
ASYNC_DATABASE_URL, _async_connect_args = _split_async_url(DATABASE_URL)

_async_kwargs: Dict[str, Any] = {"connect_args": _async_connect_args}
if not IS_SQLITE:
    _async_kwargs.update(pool_pre_ping=True, pool_recycle=300)

async_engine = create_async_engine(ASYNC_DATABASE_URL, **_async_kwargs)

# expire_on_commit=False so ORM objects stay usable (for response serialization)
# after an awaited commit without triggering further lazy IO.
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_async_db():
    """Async DB session dependency for FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        yield session

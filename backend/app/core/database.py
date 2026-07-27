from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Shared declarative base for all models
Base = declarative_base()

# ---------------------------------------------------------------------------
# Sync engine — used by the Telegram bot (aiogram handlers run their own
# blocking SessionLocal() sessions).
# ---------------------------------------------------------------------------
DATABASE_URL = settings.database_url  # absolyut yo'l (config.py ga qarang)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Sync DB session dependency (bot / legacy use)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Async engine — used by the FastAPI web app (endpoints, simulator).
# ---------------------------------------------------------------------------
def _to_async_url(url: str) -> str:
    """Map a sync DB URL to its async driver equivalent."""
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


ASYNC_DATABASE_URL = _to_async_url(DATABASE_URL)

async_engine = create_async_engine(ASYNC_DATABASE_URL)
# expire_on_commit=False so ORM objects stay usable (for response serialization)
# after an awaited commit without triggering further lazy IO.
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_async_db():
    """Async DB session dependency for FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        yield session

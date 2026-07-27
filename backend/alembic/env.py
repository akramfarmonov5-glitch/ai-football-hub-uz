"""Alembic muhiti.

Baza manzili `settings.database_url` dan olinadi — ilova va migratsiyalar
har doim bir xil bazaga ishlashi uchun (alembic.ini da URL yozilmagan).

SQLite `ALTER TABLE` ni deyarli qo'llab-quvvatlamaydi, shuning uchun
`render_as_batch=True` yoqilgan: Alembic ustun o'zgartirishlarini jadvalni
qayta yaratish orqali bajaradi.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# `alembic` buyrug'i backend/ dan tashqarida ishga tushirilsa ham import ishlasin
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
import app.models  # noqa: F401,E402  — modellar Base.metadata ga ro'yxatdan o'tsin

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate shu metadata bilan solishtiradi
target_metadata = Base.metadata

# Migratsiyalar sinxron drayver bilan bajariladi (aiosqlite kerak emas)
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Ulanishsiz rejim — SQL matnini chiqaradi (`alembic upgrade head --sql`)."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Bazaga ulanib bajariladigan odatiy rejim."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

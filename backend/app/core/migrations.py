"""Baza migratsiyalarini qo'llash.

Ilova ishga tushganda sxema avtomatik yangilanadi. Ilgari bu `create_all`
orqali qilinardi — u faqat yo'q jadvallarni yaratardi, mavjud jadvalga ustun
qo'shilsa esa hech narsa qilmasdi va xato jimgina yashirin qolardi.

Eski bazalar bilan moslik: Alembicdan oldin yaratilgan bazalarda jadvallar bor,
lekin `alembic_version` yo'q. Bunday bazada to'g'ridan-to'g'ri `upgrade` qilsak
"table already exists" xatosi chiqardi. Shuning uchun avval boshlang'ich
revizyada `stamp` qilinadi, keyin qolgan migratsiyalar qo'llanadi.
"""

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect

from app.core.config import BACKEND_DIR
from app.core.database import engine

logger = logging.getLogger(__name__)

ALEMBIC_INI = BACKEND_DIR / "alembic.ini"

# Alembicdan oldin ham mavjud bo'lgan jadval — eski bazani aniqlash uchun
LEGACY_TABLE = "matches"


def _alembic_config() -> Config:
    config = Config(str(ALEMBIC_INI))
    # Ish katalogi qanday bo'lishidan qat'i nazar skriptlar topilsin
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


def _base_revision(config: Config) -> str | None:
    """Migratsiyalar zanjiridagi eng birinchi revizya."""
    script = ScriptDirectory.from_config(config)
    bases = script.get_bases()
    return bases[0] if bases else None


def run_migrations() -> None:
    """`alembic upgrade head`. Bloklovchi — `asyncio.to_thread` orqali chaqiring."""
    if not ALEMBIC_INI.exists():
        logger.error("alembic.ini topilmadi: %s", ALEMBIC_INI)
        return

    config = _alembic_config()

    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names())

    is_legacy_database = LEGACY_TABLE in tables and "alembic_version" not in tables

    if is_legacy_database:
        base = _base_revision(config)
        if base:
            logger.info(
                "Alembicdan oldingi baza aniqlandi — %s revizyasida belgilanmoqda", base
            )
            command.stamp(config, base)

    command.upgrade(config, "head")
    logger.info("Baza sxemasi dolzarb (alembic upgrade head)")

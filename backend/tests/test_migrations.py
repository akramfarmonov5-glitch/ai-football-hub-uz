"""Migratsiyalar modellarga mos bo'lishi va eski bazani buzmasligi.

Eng muhim tekshiruv — birinchisi: modelga ustun qo'shib, migratsiya yozishni
unutsangiz, test yiqiladi. Aks holda xato faqat deploydan keyin bilinardi.
"""

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text

from app.core.database import Base, engine
from app.core.migrations import run_migrations
import app.models  # noqa: F401 — modellar Base.metadata ga tushsin


def _clean_database() -> None:
    """Bazani butunlay bo'shatadi (alembic_version ham)."""
    Base.metadata.drop_all(engine)
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        connection.commit()


def test_migratsiyalar_modellarga_mos():
    """`alembic upgrade head` natijasi modellar bilan bir xil sxema berishi kerak."""
    _clean_database()
    run_migrations()

    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection, opts={"compare_type": True, "render_as_batch": True}
        )
        differences = compare_metadata(context, Base.metadata)

    assert differences == [], (
        "Modellar va migratsiyalar farq qilmoqda. Yangi migratsiya yarating:\n"
        "  python -m alembic revision --autogenerate -m 'izoh'\n"
        f"Farqlar: {differences}"
    )


def test_bosh_bazada_barcha_jadval_yaratiladi():
    _clean_database()
    run_migrations()

    tables = set(inspect(engine).get_table_names())
    assert {"matches", "news", "users", "alembic_version"} <= tables


def test_eski_baza_stamp_qilinadi():
    """Alembicdan oldin yaratilgan bazada `upgrade` xato bermasligi kerak.

    Bunday bazada jadvallar bor, lekin `alembic_version` yo'q — to'g'ridan-to'g'ri
    upgrade "table already exists" bilan yiqilardi.
    """
    _clean_database()
    Base.metadata.create_all(engine)  # Alembicdan oldingi holatni taqlid qilamiz

    with engine.connect() as connection:
        assert "alembic_version" not in inspect(connection).get_table_names()

    run_migrations()  # xato bermasligi kerak

    with engine.connect() as connection:
        version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert version, "baza revizya bilan belgilanmadi"


def test_qayta_ishga_tushirish_xavfsiz():
    """Migratsiyalarni ikki marta qo'llash hech narsani buzmasligi kerak."""
    _clean_database()
    run_migrations()
    run_migrations()

    tables = set(inspect(engine).get_table_names())
    assert {"matches", "news", "users"} <= tables

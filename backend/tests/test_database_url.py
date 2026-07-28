"""Ulanish satrini asinxron drayverga o'girish.

Eng nozik joy: `asyncpg` `sslmode` kabi parametrlarni qabul qilmaydi, Neon
esa ulanish satrini aynan shu parametr bilan beradi. Noto'g'ri o'girilsa
ilova ishga tushmaydi — shuning uchun alohida tekshiriladi.
"""

import pytest

from app.core.database import _normalize_scheme, _split_async_url


# ---------------------------------------------------------------------------
# Sxema
# ---------------------------------------------------------------------------


def test_eski_postgres_sxemasi_tuzatiladi():
    """Ba'zi hostinglar `postgres://` beradi, SQLAlchemy `postgresql://` kutadi."""
    assert (
        _normalize_scheme("postgres://u:p@host/db") == "postgresql://u:p@host/db"
    )


def test_togri_sxema_tegilmaydi():
    assert _normalize_scheme("postgresql://u:p@host/db") == "postgresql://u:p@host/db"
    assert _normalize_scheme("sqlite:///a.db") == "sqlite:///a.db"


# ---------------------------------------------------------------------------
# SQLite
# ---------------------------------------------------------------------------


def test_sqlite_aiosqlite_ga_ogiriladi():
    url, args = _split_async_url("sqlite:///C:/loyiha/futbol.db")
    assert url == "sqlite+aiosqlite:///C:/loyiha/futbol.db"
    assert args == {}


# ---------------------------------------------------------------------------
# PostgreSQL / Neon
# ---------------------------------------------------------------------------


def test_neon_sslmode_olib_tashlanadi():
    """`sslmode` URL'da qolsa asyncpg "unexpected keyword argument" beradi."""
    url, args = _split_async_url(
        "postgresql://u:p@ep-x.aws.neon.tech/db?sslmode=require"
    )
    assert url.startswith("postgresql+asyncpg://")
    assert "sslmode" not in url
    assert args == {"ssl": True}


def test_neon_channel_binding_ham_olinadi():
    url, args = _split_async_url(
        "postgresql://u:p@host/db?sslmode=require&channel_binding=require"
    )
    assert "channel_binding" not in url
    assert "sslmode" not in url
    assert args == {"ssl": True}


def test_ssl_talab_qilinmasa_qoshilmaydi():
    _, args = _split_async_url("postgresql://u:p@localhost/db?sslmode=disable")
    assert args == {}


def test_parametrsiz_postgres():
    url, args = _split_async_url("postgresql://u:p@localhost:5432/db")
    assert url == "postgresql+asyncpg://u:p@localhost:5432/db"
    assert args == {}


def test_begona_parametrlar_saqlanadi():
    """Faqat drayver tushunmaydiganlari olinadi, qolgani qoladi."""
    url, _ = _split_async_url(
        "postgresql://u:p@host/db?sslmode=require&application_name=futbol"
    )
    assert "application_name=futbol" in url


def test_parol_va_port_buzilmaydi():
    url, _ = _split_async_url(
        "postgresql://foydalanuvchi:m2rakkab-Parol@ep-x.aws.neon.tech:5432/futbol?sslmode=require"
    )
    assert "foydalanuvchi:m2rakkab-Parol@ep-x.aws.neon.tech:5432" in url
    assert url.endswith("/futbol")


@pytest.mark.parametrize(
    "sslmode,ssl_kerakmi",
    [
        ("require", True),
        ("verify-full", True),
        ("prefer", True),
        ("disable", False),
        ("allow", False),
    ],
)
def test_sslmode_qiymatlari(sslmode, ssl_kerakmi):
    _, args = _split_async_url(f"postgresql://u:p@host/db?sslmode={sslmode}")
    assert bool(args) is ssl_kerakmi

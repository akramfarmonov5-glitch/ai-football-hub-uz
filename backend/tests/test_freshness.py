"""Sayt "bugungi" ko'rinishda qolishi.

Ikki mexanizm tekshiriladi:
  * `days` oynasi — bosh sahifada haftalar oldingi o'yinlar chiqmasligi
  * avtomatik yangilik — "Qaynoq Xabarlar" bir maqolada qotib qolmasligi
"""

from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.clock import utcnow
from app.main import app
from app.models.match import Match
from app.models.news import News
from app.services.simulator import generate_match_report


def _match(home, away, match_time, status="FT", sh=1, sa=0, league_id=39):
    return Match(
        league_id=league_id,
        league_name="EPL",
        home_team_name=home,
        away_team_name=away,
        score_home=sh,
        score_away=sa,
        status=status,
        match_time=match_time,
    )


# ---------------------------------------------------------------------------
# `days` oynasi
# ---------------------------------------------------------------------------


@pytest.fixture
async def client(db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def test_days_oynasi_eski_oyinlarni_chiqarmaydi(db, client):
    now = utcnow()
    db.add_all(
        [
            _match("Bugun", "B", now - timedelta(hours=2)),
            _match("Kecha", "B", now - timedelta(days=1)),
            _match("Eski", "B", now - timedelta(days=22)),
        ]
    )
    await db.commit()

    res = await client.get("/api/v1/matches/?days=2")
    assert res.status_code == 200
    nomlar = {m["home_team_name"] for m in res.json()}

    assert "Bugun" in nomlar and "Kecha" in nomlar
    assert "Eski" not in nomlar, "22 kunlik o'yin oynadan tashqarida qolishi kerak"


async def test_days_kelajakdagi_oyinlarni_ham_qamraydi(db, client):
    now = utcnow()
    db.add_all(
        [
            _match("Ertaga", "B", now + timedelta(hours=20), status="NS"),
            _match("Keyingi oy", "B", now + timedelta(days=30), status="NS"),
        ]
    )
    await db.commit()

    nomlar = {m["home_team_name"] for m in (await client.get("/api/v1/matches/?days=2")).json()}
    assert "Ertaga" in nomlar
    assert "Keyingi oy" not in nomlar


async def test_days_berilmasa_hamma_oyin_qaytadi(db, client):
    """Eski o'yinlar bazada qoladi — turnir jadvali ularga tayanadi."""
    now = utcnow()
    db.add_all(
        [
            _match("Bugun", "B", now),
            _match("Eski", "B", now - timedelta(days=22)),
        ]
    )
    await db.commit()

    nomlar = {m["home_team_name"] for m in (await client.get("/api/v1/matches/")).json()}
    assert nomlar == {"Bugun", "Eski"}


async def test_eski_oyin_turnir_jadvalida_qoladi(db, client):
    """Oyna faqat ko'rsatishga ta'sir qiladi, hisobga emas."""
    db.add(_match("Eski", "B", utcnow() - timedelta(days=22), sh=3, sa=0))
    await db.commit()

    tables = (await client.get("/api/v1/standings/")).json()
    jamoalar = {r["team"] for t in tables for r in t["table"]}
    assert "Eski" in jamoalar


@pytest.mark.parametrize("noto_gri", [0, -1, 400])
async def test_days_notogri_qiymatda_422(client, noto_gri):
    res = await client.get(f"/api/v1/matches/?days={noto_gri}")
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Avtomatik yangilik
# ---------------------------------------------------------------------------


async def test_yangilik_yozilmaydi_agar_oyin_bolmasa(db):
    assert await generate_match_report(db) is None


async def test_tugagan_oyindan_yangilik_yoziladi(db):
    match = _match("Arsenal", "Chelsea", utcnow() - timedelta(hours=1), sh=2, sa=1)
    db.add(match)
    await db.commit()

    news = await generate_match_report(db)
    assert news is not None
    assert news.is_published
    assert news.slug, "slug bo'sh bo'lmasligi kerak"
    # Qaysi o'yin haqida ekani teglarda qoladi
    assert f"match-{match.id}" in news.tags


async def test_ayni_oyin_haqida_ikki_marta_yozilmaydi(db):
    db.add(_match("Arsenal", "Chelsea", utcnow() - timedelta(hours=1)))
    await db.commit()

    birinchi = await generate_match_report(db)
    assert birinchi is not None

    # Yangi o'yin yo'q — takroriy maqola chiqmasligi kerak
    ikkinchi = await generate_match_report(db)
    assert ikkinchi is None


async def test_yangi_oyin_tugasa_yangi_maqola(db):
    """Oxirgi maqoladan keyin tugagan o'yin bo'lsa, yangi maqola yoziladi."""
    eski_vaqt = utcnow() - timedelta(days=1)
    db.add(News(title="Eski maqola", slug="eski-maqola", content="...", created_at=eski_vaqt))
    db.add(_match("Arsenal", "Chelsea", utcnow() - timedelta(minutes=30)))
    await db.commit()

    news = await generate_match_report(db)
    assert news is not None, "eski maqoladan keyin tugagan o'yin bor edi"


async def test_yaqinda_yozilgan_bolsa_kutiladi(db):
    """AI so'rovlari cheklanishi uchun maqolalar tez-tez yozilmaydi."""
    db.add(News(title="Yangi", slug="yangi", content="...", created_at=utcnow()))
    db.add(_match("Arsenal", "Chelsea", utcnow() - timedelta(minutes=5)))
    await db.commit()

    assert await generate_match_report(db) is None


async def test_tugamagan_oyin_haqida_yozilmaydi(db):
    db.add(_match("Arsenal", "Chelsea", utcnow() - timedelta(minutes=10), status="LIVE"))
    await db.commit()

    assert await generate_match_report(db) is None

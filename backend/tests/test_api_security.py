"""API xavfsizligi: yozish endpointlari tokensiz ishlamasligi kerak.

Ilgari POST /api/v1/news/ ochiq edi — har kim saytga maqola chop eta olardi.
Bu testlar shu teshik qaytib ochilmasligini kafolatlaydi.
"""

import httpx
import pytest
import pytest_asyncio

from app.core.database import Base, async_engine
from app.main import app
from tests.conftest import TEST_ADMIN_TOKEN


@pytest_asyncio.fixture
async def client():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # `lifespan` ni ishga tushirmaymiz — fon simulyatori testlarga xalaqit bermasin
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


WRITE_ENDPOINTS = [
    ("POST", "/api/v1/news/", {"title": "Test", "content": "matn"}),
    ("POST", "/api/v1/matches/1/preview", None),
    ("POST", "/api/v1/matches/1/analysis", None),
    ("POST", "/api/v1/admin/seed", None),
    ("POST", "/api/v1/admin/simulate", None),
    ("GET", "/api/v1/admin/verify", None),
]


@pytest.mark.parametrize("method,path,payload", WRITE_ENDPOINTS)
async def test_tokensiz_rad_etiladi(client, method, path, payload):
    response = await client.request(method, path, json=payload)
    assert response.status_code == 401, f"{method} {path} himoyalanmagan!"


@pytest.mark.parametrize("method,path,payload", WRITE_ENDPOINTS)
async def test_notogri_token_rad_etiladi(client, method, path, payload):
    response = await client.request(
        method, path, json=payload, headers={"X-Admin-Token": "admin123"}
    )
    assert response.status_code == 401


async def test_togri_token_ishlaydi(client):
    response = await client.get(
        "/api/v1/admin/verify", headers={"X-Admin-Token": TEST_ADMIN_TOKEN}
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


async def test_ommaviy_oqish_ochiq_qoladi(client):
    """Auth qo'shilgani o'qishni buzmasligi kerak."""
    for path in ("/api/v1/matches/", "/api/v1/news/", "/api/v1/matches/live", "/health", "/"):
        response = await client.get(path)
        assert response.status_code == 200, path


async def test_notogri_status_qabul_qilinmaydi(client):
    """Admin override faqat NS/LIVE/FT qabul qiladi."""
    response = await client.put(
        "/api/v1/admin/matches/1",
        json={"score_home": 1, "score_away": 0, "status": "XATO", "minute": 10},
        headers={"X-Admin-Token": TEST_ADMIN_TOKEN},
    )
    assert response.status_code == 422


async def test_manfiy_hisob_qabul_qilinmaydi(client):
    response = await client.put(
        "/api/v1/admin/matches/1",
        json={"score_home": -5, "score_away": 0, "status": "LIVE", "minute": 10},
        headers={"X-Admin-Token": TEST_ADMIN_TOKEN},
    )
    assert response.status_code == 422


async def test_limit_chegarasi_ishlaydi(client):
    assert (await client.get("/api/v1/matches/?limit=999")).status_code == 422
    assert (await client.get("/api/v1/matches/?limit=50")).status_code == 200

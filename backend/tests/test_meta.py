"""Ma'lumot manbai to'g'ri e'lon qilinishi.

Bu ogohlantirish tizimining asosi: agar `is_simulated` noto'g'ri qaytsa,
sayt to'qib chiqarilgan natijalarni haqiqiy deb ko'rsatib qo'yadi.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


async def test_kalitsiz_simulyatsiya_deb_qaytadi(client):
    """Testlarda API_FOOTBALL_KEY bo'sh (conftest) — demak simulyatsiya."""
    res = await client.get("/api/v1/meta/")
    assert res.status_code == 200

    data = res.json()
    assert data["is_simulated"] is True
    assert data["data_source"] == "simulation"


async def test_kalit_bolsa_real_manba(monkeypatch):
    """Kalit qo'yilganda manba "api-football" bo'lishi kerak."""
    from app.api.endpoints import meta

    monkeypatch.setattr(meta, "settings", Settings(API_FOOTBALL_KEY="test-kalit"))
    data = await meta.read_meta()

    assert data["is_simulated"] is False
    assert data["data_source"] == "api-football"


async def test_ai_holati_korsatiladi(monkeypatch):
    from app.api.endpoints import meta

    monkeypatch.setattr(meta, "settings", Settings(GEMINI_API_KEY=""))
    assert (await meta.read_meta())["ai_enabled"] is False

    monkeypatch.setattr(meta, "settings", Settings(GEMINI_API_KEY="kalit"))
    assert (await meta.read_meta())["ai_enabled"] is True


async def test_vertex_ham_ai_hisoblanadi(monkeypatch):
    """Faqat Vertex sozlangan bo'lsa ham AI yoqilgan deb hisoblanadi."""
    from app.api.endpoints import meta

    monkeypatch.setattr(
        meta, "settings", Settings(GEMINI_API_KEY="", GCP_PROJECT_ID="loyiha-123")
    )
    assert (await meta.read_meta())["ai_enabled"] is True

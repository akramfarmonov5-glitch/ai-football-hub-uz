"""Jamoa tavsiflarini o'zbekchaga o'girish.

Tarmoqqa chiqilmaydi — AI dvigateli soxta javob beradi.
"""

import pytest

from app.models.team import Team
from app.services.ai_engine import AIEngineService, Provider
from app.services.simulator import translate_team_descriptions
from app.services.teams import get_team_page


class _Javob:
    def __init__(self, text):
        self.text = text


class _SoxtaModels:
    def __init__(self, javob=None, xato=None):
        self._javob = javob
        self._xato = xato
        self.promptlar = []

    def generate_content(self, model, contents):
        self.promptlar.append(contents)
        if self._xato:
            raise self._xato
        return _Javob(self._javob)


class _SoxtaKlient:
    def __init__(self, javob=None, xato=None):
        self.models = _SoxtaModels(javob, xato)


def _engine(javob=None, xato=None) -> AIEngineService:
    engine = AIEngineService.__new__(AIEngineService)
    engine.api_key = ""
    engine.model_name = "test"
    engine.providers = [Provider("Test", _SoxtaKlient(javob, xato), "m")]
    engine._active_label = None
    engine.enabled = True
    return engine


def _team(name="Pakhtakor", **kwargs):
    kwargs.setdefault("description", "Pakhtakor is a football club from Tashkent.")
    return Team(
        id=kwargs.pop("id", 139020),
        slug=kwargs.pop("slug", "pakhtakor"),
        name=name,
        league_id=4794,
        league_name="Uzbekistan Super League",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Tarjima metodi
# ---------------------------------------------------------------------------


async def test_tarjima_qaytadi():
    engine = _engine(javob="Paxtakor — Toshkentdan futbol klubi.")
    assert await engine.translate_to_uzbek("Pakhtakor is a club.") == (
        "Paxtakor — Toshkentdan futbol klubi."
    )


async def test_bosh_matn_sorov_yubormaydi():
    engine = _engine(javob="natija")
    klient = engine.providers[0].client

    assert await engine.translate_to_uzbek("") == ""
    assert await engine.translate_to_uzbek("   ") == ""
    assert klient.models.promptlar == [], "bo'sh matn uchun so'rov ketmasligi kerak"


async def test_jamoa_nomi_promptga_qoshiladi():
    engine = _engine(javob="tarjima")
    await engine.translate_to_uzbek("text", "Pakhtakor")

    prompt = engine.providers[0].client.models.promptlar[0]
    assert "Pakhtakor" in prompt


async def test_ai_xatosida_bosh_satr():
    engine = _engine(xato=RuntimeError("429"))
    assert await engine.translate_to_uzbek("text") == ""


# ---------------------------------------------------------------------------
# Fon vazifasi
# ---------------------------------------------------------------------------


async def test_tavsif_tarjima_qilinadi(db, monkeypatch):
    from app.services import simulator

    monkeypatch.setattr(simulator, "get_ai_engine", lambda: _engine(javob="O'zbekcha matn"))

    db.add(_team())
    await db.commit()

    assert await translate_team_descriptions(db) == 1

    team = await db.get(Team, 139020)
    assert team.description_uz == "O'zbekcha matn"
    assert team.description, "asl matn saqlanib qolishi kerak"


async def test_tarjima_qilinganlar_qayta_olinmaydi(db, monkeypatch):
    from app.services import simulator

    monkeypatch.setattr(simulator, "get_ai_engine", lambda: _engine(javob="yangi"))

    db.add(_team(description_uz="allaqachon tarjima qilingan"))
    await db.commit()

    assert await translate_team_descriptions(db) == 0

    team = await db.get(Team, 139020)
    assert team.description_uz == "allaqachon tarjima qilingan"


async def test_tavsifsiz_jamoa_otkazib_yuboriladi(db, monkeypatch):
    from app.services import simulator

    monkeypatch.setattr(simulator, "get_ai_engine", lambda: _engine(javob="matn"))

    db.add(_team(description=None))
    await db.commit()

    assert await translate_team_descriptions(db) == 0


async def test_ai_ishlamasa_asl_matn_qoladi(db, monkeypatch):
    """AI xato bersa tavsif yo'qolmasligi kerak."""
    from app.services import simulator

    monkeypatch.setattr(simulator, "get_ai_engine", lambda: _engine(xato=RuntimeError("x")))

    db.add(_team())
    await db.commit()

    assert await translate_team_descriptions(db) == 0

    team = await db.get(Team, 139020)
    assert team.description_uz is None
    assert team.description, "asl matn joyida qolishi kerak"


async def test_bir_qadamda_cheklangan_son(db, monkeypatch):
    """Bir vaqtda o'nlab AI so'rovi ketmasligi kerak."""
    from app.services import simulator

    monkeypatch.setattr(simulator, "get_ai_engine", lambda: _engine(javob="matn"))
    monkeypatch.setattr(simulator, "TRANSLATIONS_PER_TICK", 2)

    db.add_all([_team(f"Jamoa {i}", id=i, slug=f"jamoa-{i}") for i in range(1, 6)])
    await db.commit()

    assert await translate_team_descriptions(db) == 2


# ---------------------------------------------------------------------------
# Sahifada ko'rsatish
# ---------------------------------------------------------------------------


async def test_sahifa_tarjimani_korsatadi(db):
    db.add(_team(description_uz="O'zbekcha tavsif"))
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["description"] == "O'zbekcha tavsif"
    assert page["description_translated"] is True


async def test_tarjima_yoq_bolsa_asl_matn(db):
    db.add(_team(description="English description"))
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["description"] == "English description"
    assert page["description_translated"] is False, (
        "asl matn tarjima deb belgilanmasligi kerak"
    )

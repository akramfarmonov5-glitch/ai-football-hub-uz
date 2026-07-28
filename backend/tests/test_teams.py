"""Jamoa sahifasi: slug barqarorligi, o'yinlar tanlovi, jadval qatori."""

from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.clock import utcnow
from app.main import app
from app.models.match import Match
from app.models.team import Team
from app.services.teams import get_team_page, list_teams, team_slug


@pytest.fixture
async def client(db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def _match(home, away, offset_hours, status="FT", sh=1, sa=0, league_id=4794):
    return Match(
        league_id=league_id,
        league_name="Uzbekistan Super League",
        home_team_name=home,
        away_team_name=away,
        score_home=sh,
        score_away=sa,
        status=status,
        match_time=utcnow() + timedelta(hours=offset_hours),
    )


def _team(name="Pakhtakor", **kwargs):
    return Team(
        id=kwargs.pop("id", 139020),
        slug=team_slug(name),
        name=name,
        league_id=kwargs.pop("league_id", 4794),
        league_name="Uzbekistan Super League",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "nom,kutilgan",
    [
        ("Pakhtakor", "pakhtakor"),
        ("Neftchi Fergana", "neftchi-fergana"),
        ("Mash'al Mubarek", "mashal-mubarek"),
        ("Lokomotiv Tashkent", "lokomotiv-tashkent"),
        ("Sogdiana Jizzakh", "sogdiana-jizzakh"),
        # Turli apostrof belgilari bir xil natija berishi kerak
        ("Mash’al Mubarek", "mashal-mubarek"),
        # Diakritik belgilar tashlanmaydi, lotinga o'giriladi
        ("Fenerbahçe", "fenerbahce"),
        ("Atlético Madrid", "atletico-madrid"),
        ("Górnik Zabrze", "gornik-zabrze"),
        ("Bayern München", "bayern-munchen"),
        # Normalizatsiya ajratmaydigan harflar
        ("Łódź", "lodz"),
        ("Malmö FF", "malmo-ff"),
    ],
)
def test_slug_yasaladi(nom, kutilgan):
    assert team_slug(nom) == kutilgan


def test_slug_bosh_nomda_ham_ishlaydi():
    """Slug hech qachon bo'sh bo'lmasligi kerak — aks holda URL buziladi."""
    assert team_slug("") == "jamoa"
    assert team_slug("!!!") == "jamoa"


def test_slug_barqaror():
    """Bir xil kiritma har doim bir xil natija — havolalar buzilmasligi uchun."""
    assert team_slug("Neftchi Fergana") == team_slug("Neftchi Fergana")


# ---------------------------------------------------------------------------
# Sahifa ma'lumoti
# ---------------------------------------------------------------------------


async def test_topilmagan_jamoa_none(db):
    assert await get_team_page(db, "yoq-jamoa") is None


async def test_profilsiz_ham_sahifa_ishlaydi(db):
    """Profillar bosqichma-bosqich yuklanadi. Turnir jadvali va o'yin
    kartalari hamma jamoani havola qiladi, shuning uchun profili hali
    yo'q jamoa ham 404 bermasligi kerak."""
    db.add_all(
        [
            _match("Neftchi Fergana", "Nasaf", -24, status="FT", sh=2, sa=1),
            _match("Buxoro", "Neftchi Fergana", 12, status="NS"),
        ]
    )
    await db.commit()

    page = await get_team_page(db, "neftchi-fergana")
    assert page is not None, "profilsiz jamoa ham topilishi kerak"
    assert page["name"] == "Neftchi Fergana"
    assert page["slug"] == "neftchi-fergana"
    assert len(page["recent_matches"]) == 1
    assert len(page["upcoming_matches"]) == 1
    # Profil maydonlari bo'sh, lekin sahifa buzilmaydi
    assert page["stadium"] is None
    assert page["description"] is None


async def test_profilsiz_jamoa_ligasi_oyindan_olinadi(db):
    db.add(_match("Neftchi Fergana", "Nasaf", -5, status="FT"))
    await db.commit()

    page = await get_team_page(db, "neftchi-fergana")
    assert page["league_name"] == "Uzbekistan Super League"


async def test_profil_paydo_bolgach_ustun_turadi(db):
    """Profil yuklangach uning ma'lumoti ishlatilishi kerak."""
    db.add(_match("Pakhtakor", "Nasaf", -5, status="FT"))
    db.add(_team(stadium="Paxtakor stadioni", league_id=4794))
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["stadium"] == "Paxtakor stadioni"


async def test_profil_qaytadi(db):
    db.add(_team(stadium="Paxtakor stadioni", founded=1956, stadium_capacity=35000))
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page is not None
    assert page["name"] == "Pakhtakor"
    assert page["stadium"] == "Paxtakor stadioni"
    assert page["founded"] == 1956
    assert page["stadium_capacity"] == 35000


async def test_oyinlar_ajratiladi(db):
    db.add(_team())
    db.add_all(
        [
            _match("Pakhtakor", "Buxoro", -48, status="FT", sh=2, sa=0),
            _match("AGMK", "Pakhtakor", -24, status="FT", sh=1, sa=3),
            _match("Pakhtakor", "Nasaf", 24, status="NS"),
            _match("Andijon", "Buxoro", -12, status="FT"),  # begona o'yin
        ]
    )
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert len(page["recent_matches"]) == 2, "faqat shu jamoaning tugagan o'yinlari"
    assert len(page["upcoming_matches"]) == 1


async def test_mehmondagi_oyin_ham_hisobga_olinadi(db):
    db.add(_team())
    db.add(_match("Buxoro", "Pakhtakor", -5, status="FT"))
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert len(page["recent_matches"]) == 1


async def test_tugagan_oyinlar_yangisidan_tartiblanadi(db):
    db.add(_team())
    db.add_all(
        [
            _match("Pakhtakor", "Eski", -100, status="FT"),
            _match("Pakhtakor", "Yangi", -2, status="FT"),
        ]
    )
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["recent_matches"][0].away_team_name == "Yangi"


async def test_bolajak_oyinlar_yaqinidan_tartiblanadi(db):
    db.add(_team())
    db.add_all(
        [
            _match("Pakhtakor", "Uzoq", 200, status="NS"),
            _match("Pakhtakor", "Yaqin", 3, status="NS"),
        ]
    )
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["upcoming_matches"][0].away_team_name == "Yaqin"


async def test_jonli_oyin_bolajaklar_qatorida(db):
    db.add(_team())
    db.add(_match("Pakhtakor", "Nasaf", 0, status="LIVE"))
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert len(page["upcoming_matches"]) == 1


async def test_jadval_qatori_topiladi(db):
    """Jadval simulyatsiya rejimida o'yinlardan hisoblanadi."""
    db.add(_team())
    db.add_all(
        [
            _match("Pakhtakor", "Buxoro", -48, status="FT", sh=2, sa=0),
            _match("Pakhtakor", "Nasaf", -24, status="FT", sh=1, sa=1),
        ]
    )
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["standing"] is not None
    assert page["standing"]["team"] == "Pakhtakor"
    assert page["standing"]["points"] == 4


async def test_jadvalda_bolmasa_none(db):
    db.add(_team())
    await db.commit()

    page = await get_team_page(db, "pakhtakor")
    assert page["standing"] is None


async def test_royxat_alifbo_tartibida(db):
    db.add_all([_team("Zenit", id=1), _team("AGMK", id=2), _team("Buxoro", id=3)])
    await db.commit()

    nomlar = [t["name"] for t in await list_teams(db)]
    assert nomlar == ["AGMK", "Buxoro", "Zenit"]


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


async def test_api_jamoa_sahifasi(db, client):
    db.add(_team(stadium="Paxtakor stadioni"))
    db.add(_match("Pakhtakor", "Buxoro", -3, status="FT", sh=2, sa=1))
    await db.commit()

    res = await client.get("/api/v1/teams/pakhtakor")
    assert res.status_code == 200

    data = res.json()
    assert data["name"] == "Pakhtakor"
    assert data["stadium"] == "Paxtakor stadioni"
    assert len(data["recent_matches"]) == 1
    assert data["recent_matches"][0]["home_team_name"] == "Pakhtakor"


async def test_api_topilmasa_404(db, client):
    res = await client.get("/api/v1/teams/yoq-jamoa")
    assert res.status_code == 404


async def test_api_royxat(db, client):
    db.add(_team())
    await db.commit()

    res = await client.get("/api/v1/teams/")
    assert res.status_code == 200
    assert [t["slug"] for t in res.json()] == ["pakhtakor"]

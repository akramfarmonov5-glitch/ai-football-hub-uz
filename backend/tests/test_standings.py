"""Turnir jadvali: ochko, saralash, tenglikda ajratish va forma."""

import pytest

from app.core.clock import utcnow
from app.models.match import Match
from app.services.standings import build_tables, get_standings


def _match(home, away, sh, sa, status="FT", league_id=39, league_name="EPL", **kwargs):
    return Match(
        league_id=league_id,
        league_name=league_name,
        home_team_name=home,
        away_team_name=away,
        score_home=sh,
        score_away=sa,
        status=status,
        match_time=utcnow(),
        **kwargs,
    )


def _row(table, team):
    return next(r for r in table if r["team"] == team)


def test_ochko_togri_hisoblanadi():
    tables = build_tables(
        [
            _match("A", "B", 2, 0),  # A g'alaba
            _match("B", "C", 1, 1),  # durang
            _match("C", "A", 0, 3),  # A g'alaba
        ]
    )
    table = tables[0]["table"]

    a = _row(table, "A")
    assert a["played"] == 2 and a["won"] == 2 and a["points"] == 6

    b = _row(table, "B")
    assert b["played"] == 2 and b["drawn"] == 1 and b["lost"] == 1 and b["points"] == 1

    c = _row(table, "C")
    assert c["drawn"] == 1 and c["lost"] == 1 and c["points"] == 1


def test_gollar_va_farq():
    tables = build_tables([_match("A", "B", 3, 1)])
    table = tables[0]["table"]

    a, b = _row(table, "A"), _row(table, "B")
    assert (a["goals_for"], a["goals_against"], a["goal_difference"]) == (3, 1, 2)
    assert (b["goals_for"], b["goals_against"], b["goal_difference"]) == (1, 3, -2)


def test_saralash_ochko_boyicha():
    tables = build_tables(
        [
            _match("Kuchsiz", "Kuchli", 0, 5),
            _match("Ortacha", "Kuchsiz", 1, 0),
        ]
    )
    tartib = [r["team"] for r in tables[0]["table"]]
    assert tartib[0] == "Kuchli"
    assert tartib[-1] == "Kuchsiz"


def test_ochko_teng_bolsa_gollar_farqi_ajratadi():
    tables = build_tables(
        [
            _match("A", "X", 5, 0),  # A: 3 ochko, farq +5
            _match("B", "Y", 1, 0),  # B: 3 ochko, farq +1
        ]
    )
    table = tables[0]["table"]
    assert _row(table, "A")["position"] < _row(table, "B")["position"]


def test_farq_ham_teng_bolsa_urilgan_gollar_ajratadi():
    tables = build_tables(
        [
            _match("A", "X", 3, 2),  # 3 ochko, farq +1, urilgan 3
            _match("B", "Y", 1, 0),  # 3 ochko, farq +1, urilgan 1
        ]
    )
    table = tables[0]["table"]
    assert _row(table, "A")["position"] < _row(table, "B")["position"]


def test_hammasi_teng_bolsa_alifbo_tartibi():
    """Natija barqaror bo'lishi kerak — har chaqiruvda bir xil tartib."""
    tables = build_tables([_match("Zenit", "Arsenal", 0, 0)])
    tartib = [r["team"] for r in tables[0]["table"]]
    assert tartib == ["Arsenal", "Zenit"]


def test_tugamagan_oyinlar_hisobga_olinmaydi():
    tables = build_tables(
        [
            _match("A", "B", 2, 0, status="FT"),
            _match("A", "C", 9, 0, status="LIVE"),
            _match("A", "D", 9, 0, status="NS"),
        ]
    )
    a = _row(tables[0]["table"], "A")
    assert a["played"] == 1, "faqat tugagan o'yin hisoblanadi"
    assert a["goals_for"] == 2


def test_ligalar_alohida_jadval():
    tables = build_tables(
        [
            _match("A", "B", 1, 0, league_id=39, league_name="EPL"),
            _match("C", "D", 1, 0, league_id=140, league_name="La Liga"),
        ]
    )
    assert len(tables) == 2
    nomlar = {t["league_name"] for t in tables}
    assert nomlar == {"EPL", "La Liga"}
    for t in tables:
        assert len(t["table"]) == 2, "jamoalar ligalar orasida aralashmasligi kerak"


def test_forma_oxirgi_5_oyin():
    oyinlar = [_match("A", f"R{i}", 1, 0) for i in range(4)]  # 4 ta g'alaba
    oyinlar.append(_match("A", "R4", 0, 1))  # mag'lubiyat
    oyinlar.append(_match("A", "R5", 2, 2))  # durang
    tables = build_tables(oyinlar)

    a = _row(tables[0]["table"], "A")
    assert len(a["form"]) == 5, "faqat oxirgi 5 o'yin"
    assert a["form"][-1] == "D", "eng yangi natija oxirida turishi kerak"
    assert a["form"][-2] == "L"


def test_mehmon_sifatidagi_natija_ham_hisoblanadi():
    tables = build_tables([_match("A", "B", 0, 2)])
    b = _row(tables[0]["table"], "B")
    assert b["won"] == 1 and b["points"] == 3 and b["goals_for"] == 2


def test_bosh_royxat_bosh_jadval():
    assert build_tables([]) == []


async def test_bazadan_oqiydi(db):
    db.add_all(
        [
            _match("Pakhtakor", "Navbahor", 2, 1, league_id=1000, league_name="Superliga"),
            _match("Navbahor", "Nasaf", 0, 0, league_id=1000, league_name="Superliga"),
        ]
    )
    await db.commit()

    tables = await get_standings(db)
    assert len(tables) == 1
    table = tables[0]["table"]
    assert _row(table, "Pakhtakor")["points"] == 3
    assert _row(table, "Navbahor")["points"] == 1
    assert _row(table, "Nasaf")["points"] == 1


async def test_liga_boyicha_filtr(db):
    db.add_all(
        [
            _match("A", "B", 1, 0, league_id=39, league_name="EPL"),
            _match("C", "D", 1, 0, league_id=140, league_name="La Liga"),
        ]
    )
    await db.commit()

    tables = await get_standings(db, league_id=39)
    assert len(tables) == 1
    assert tables[0]["league_name"] == "EPL"


@pytest.mark.parametrize("sh,sa,kutilgan", [(1, 0, "W"), (0, 1, "L"), (2, 2, "D")])
def test_natija_belgilari(sh, sa, kutilgan):
    tables = build_tables([_match("A", "B", sh, sa)])
    assert _row(tables[0]["table"], "A")["form"] == [kutilgan]

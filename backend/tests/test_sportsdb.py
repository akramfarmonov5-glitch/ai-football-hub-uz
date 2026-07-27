"""TheSportsDB moslamasi: javobni loyiha modeliga o'girish.

Testlar tarmoqqa chiqmaydi — haqiqiy API javobining nusxasi ishlatiladi
(2026-07-27 da olingan).
"""

from datetime import datetime

import pytest

from app.services.sportsdb import SportsDBService

# Haqiqiy javobdan olingan namuna
TUGAGAN_OYIN = {
    "idEvent": "2426717",
    "idLeague": "4794",
    "strLeague": "Uzbekistan Super League",
    "strHomeTeam": "AGMK",
    "strAwayTeam": "Mash'al Mubarek",
    "strHomeTeamBadge": "https://r2.thesportsdb.com/images/media/team/badge/35f4.png",
    "strAwayTeamBadge": "https://r2.thesportsdb.com/images/media/team/badge/aw16.png",
    "intHomeScore": 2,
    "intAwayScore": 1,
    "strStatus": "FT",
    "dateEvent": "2026-07-27",
    "strTime": "15:00:00",
    "strTimestamp": "2026-07-27T15:00:00",
    "strPostponed": "no",
}

BOSHLANMAGAN_OYIN = {
    "idEvent": "2426715",
    "idLeague": "4794",
    "strLeague": "Uzbekistan Super League",
    "strHomeTeam": "Nasaf",
    "strAwayTeam": "Qizilqum Zarafshon",
    "intHomeScore": None,
    "intAwayScore": None,
    "strStatus": "NS",
    "dateEvent": "2026-07-28",
    "strTimestamp": "2026-07-28T15:00:00",
    "strPostponed": "no",
}

JADVAL_QATORI = {
    "idLeague": "4794",
    "strLeague": "Uzbekistan Super League",
    "strTeam": "Neftchi Fergana",
    "strBadge": "https://www.thesportsdb.com/images/media/team/badge/emqz.png",
    "intRank": "1",
    "intPlayed": "13",
    "intWin": "11",
    "intDraw": "1",
    "intLoss": "1",
    "intGoalsFor": "32",
    "intGoalsAgainst": "5",
    "intGoalDifference": "27",
    "intPoints": "34",
    "strForm": "WWDWW",
}


@pytest.fixture
def service(db):
    return SportsDBService(db)


def test_tugagan_oyin_ogiriladi(service):
    match = service._to_match(TUGAGAN_OYIN)

    assert match is not None
    assert match.id == 2426717
    assert match.status == "FT"
    assert (match.score_home, match.score_away) == (2, 1)
    assert match.home_team_name == "AGMK"
    assert match.league_name == "Uzbekistan Super League"
    assert match.home_team_logo.startswith("https://")
    # strTimestamp UTC da (strTimeLocal alohida) — naive UTC bo'lib saqlanadi
    assert match.match_time == datetime(2026, 7, 27, 15, 0)


def test_boshlanmagan_oyin_ogiriladi(service):
    match = service._to_match(BOSHLANMAGAN_OYIN)

    assert match is not None
    assert match.status == "NS"
    assert (match.score_home, match.score_away) == (0, 0)


def test_qoldirilgan_oyin_tashlab_ketiladi(service):
    """Qoldirilgan o'yin jadvalda chalkashlik keltiradi."""
    assert service._to_match({**TUGAGAN_OYIN, "strPostponed": "yes"}) is None


def test_idsiz_yozuv_tashlab_ketiladi(service):
    assert service._to_match({**TUGAGAN_OYIN, "idEvent": None}) is None
    assert service._to_match({**TUGAGAN_OYIN, "idEvent": "abc"}) is None


def test_vaqtsiz_yozuv_tashlab_ketiladi(service):
    buzuq = {k: v for k, v in TUGAGAN_OYIN.items() if k not in ("strTimestamp", "dateEvent")}
    assert service._to_match(buzuq) is None


@pytest.mark.parametrize(
    "status,hisob_bor,kutilgan",
    [
        ("FT", True, "FT"),
        ("Match Finished", True, "FT"),
        ("AET", True, "FT"),
        ("NS", False, "NS"),
        ("1H", True, "LIVE"),
        ("HT", True, "LIVE"),
        # Status bo'sh: hisobga qarab hal qilinadi
        ("", True, "FT"),
        ("", False, "NS"),
        (None, False, "NS"),
    ],
)
def test_holatlar_ogiriladi(service, status, hisob_bor, kutilgan):
    assert service._map_status(status, hisob_bor) == kutilgan


def test_jadval_qatori_ogiriladi(service):
    row = service._to_standing_row(JADVAL_QATORI)

    assert row["position"] == 1
    assert row["team"] == "Neftchi Fergana"
    assert row["points"] == 34
    assert row["played"] == 13
    assert row["goal_difference"] == 27
    assert row["form"] == ["W", "W", "D", "W", "W"]


def test_jadval_qatori_bosh_qiymatlarga_chidaydi(service):
    row = service._to_standing_row({"strTeam": "X"})

    assert row["points"] == 0 and row["played"] == 0
    assert row["form"] == []


def test_forma_oxirgi_5_ta(service):
    row = service._to_standing_row({**JADVAL_QATORI, "strForm": "WWWWWWWLDL"})
    assert len(row["form"]) == 5
    assert row["form"] == ["W", "W", "L", "D", "L"]


def test_ochirilgan_bolsa_ishlamaydi(db, monkeypatch):
    """conftest da SPORTSDB_ENABLED=false — testlar tarmoqqa chiqmasligi kerak."""
    service = SportsDBService(db)
    assert service.enabled is False


async def test_ochirilgan_holatda_bosh_royxat(db):
    service = SportsDBService(db)
    assert await service.sync_matches() == []
    assert await service.fetch_standings() == []

"""Vaqt zonasi kelishuvi: bazada naive UTC, javobda timezone bilan.

Bu bo'lmasa brauzer timezone'siz ISO satrni mahalliy vaqt deb o'qib,
O'zbekistonda o'yin vaqtlarini 5 soatga siljitib ko'rsatardi.
"""

from datetime import datetime, timedelta, timezone

from app.core.clock import as_utc, to_naive_utc, utcnow
from app.schemas.match import MatchResponse


def test_utcnow_naive_va_utc():
    now = utcnow()
    assert now.tzinfo is None, "bazaga naive qiymat yozilishi kerak"
    # Haqiqiy UTC bilan farq juda kichik bo'lishi kerak
    delta = abs(now - datetime.now(timezone.utc).replace(tzinfo=None))
    assert delta < timedelta(seconds=5)


def test_as_utc_belgi_qoshadi():
    naive = datetime(2026, 7, 5, 4, 14, 37)
    aware = as_utc(naive)
    assert aware.tzinfo == timezone.utc
    assert aware.isoformat() == "2026-07-05T04:14:37+00:00"


def test_as_utc_boshqa_zonani_ogiradi():
    tashkent = timezone(timedelta(hours=5))
    aware = as_utc(datetime(2026, 7, 5, 9, 14, 37, tzinfo=tashkent))
    assert aware.hour == 4, "Toshkent 09:14 -> UTC 04:14"


def test_to_naive_utc():
    tashkent = timezone(timedelta(hours=5))
    naive = to_naive_utc(datetime(2026, 7, 5, 9, 14, 37, tzinfo=tashkent))
    assert naive.tzinfo is None
    assert naive.hour == 4


def test_none_qiymat_xato_bermaydi():
    assert as_utc(None) is None
    assert to_naive_utc(None) is None


def test_javobda_timezone_belgisi_bor():
    """Eng muhim tekshiruv: API javobidagi vaqt timezone bilan chiqadi."""
    response = MatchResponse(
        id=1,
        league_id=39,
        league_name="EPL",
        home_team_name="Arsenal",
        away_team_name="Chelsea",
        status="LIVE",
        score_home=1,
        score_away=0,
        match_time=datetime(2026, 7, 5, 4, 14, 37),  # naive, bazadan kelgandek
        minute=42,
    )
    serialized = response.model_dump_json()
    assert "+00:00" in serialized or "Z" in serialized, serialized

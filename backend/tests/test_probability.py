"""G'alaba ehtimoli. Asosiy kafolat: manfiy foiz yo'q, yig'indi aniq 100.

Ilgari bu hisob bir necha joyda takrorlangan edi va 4:0 kabi hisobda
`away = 15 - 20 = -5%` chiqib, progress-bar buzilardi.
"""

import pytest

from app.services.probability import estimate_win_probability


@pytest.mark.parametrize("home", range(0, 7))
@pytest.mark.parametrize("away", range(0, 7))
@pytest.mark.parametrize("minute", [0, 1, 15, 45, 70, 89, 90])
@pytest.mark.parametrize("status", ["NS", "LIVE", "FT"])
def test_har_doim_musbat_va_yigindi_100(home, away, minute, status):
    p = estimate_win_probability(home, away, minute, status)

    assert set(p) == {"home", "draw", "away"}
    assert min(p.values()) >= 0, f"manfiy foiz: {p}"
    assert sum(p.values()) == 100, f"yig'indi 100 emas: {p}"


def test_tugagan_oyin_natijasi_aniq():
    assert estimate_win_probability(2, 1, 90, "FT") == {"home": 100, "draw": 0, "away": 0}
    assert estimate_win_probability(0, 3, 90, "FT") == {"home": 0, "draw": 0, "away": 100}
    assert estimate_win_probability(1, 1, 90, "FT") == {"home": 0, "draw": 100, "away": 0}


def test_oldinda_borgan_jamoa_ustun():
    p = estimate_win_probability(2, 0, 70, "LIVE")
    assert p["home"] > p["away"]
    assert p["home"] > p["draw"]


def test_vaqt_otgani_sari_ishonch_ortadi():
    """Bir xil hisob, lekin o'yin oxiriga yaqinroq — ehtimol qat'iyroq."""
    erta = estimate_win_probability(1, 0, 10, "LIVE")
    kech = estimate_win_probability(1, 0, 85, "LIVE")
    assert kech["home"] > erta["home"]


def test_hisob_teng_bolganda_muvozanat():
    p = estimate_win_probability(1, 1, 45, "LIVE")
    # O'z maydoni afzalligi sababli mezbon biroz oldinda bo'lishi mumkin,
    # lekin farq katta bo'lmasligi kerak
    assert abs(p["home"] - p["away"]) <= 10

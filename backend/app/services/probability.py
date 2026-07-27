"""G'alaba ehtimolini hisoblash.

Ilgari ehtimollar bir necha joyda qo'lda hisoblanardi va katta hisob farqida
manfiy qiymat chiqib ketardi (masalan 4:0 da `away = 15 - 4*5 = -5%`), bu esa
frontenddagi progress-bar'ni buzardi. Endi bitta funksiya:
qiymatlar har doim musbat va yig'indisi aniq 100.
"""

from typing import Dict

# O'z maydonida o'ynash afzalligi hisobga olingan boshlang'ich taqsimot
BASE_HOME, BASE_DRAW, BASE_AWAY = 40.0, 27.0, 33.0

# Har bir gol farqi ehtimolni qanchalik siljitishi
GOAL_WEIGHT = 16.0

# Hech bir natija butunlay imkonsiz deb ko'rsatilmaydi
MIN_PERCENT = 1


def estimate_win_probability(
    score_home: int,
    score_away: int,
    minute: int = 0,
    status: str = "LIVE",
) -> Dict[str, int]:
    """Hisob va o'tgan vaqtga qarab {home, draw, away} foizlarini qaytaradi.

    O'yin oxiriga qanchalik yaqin bo'lsa, mavjud hisob shunchalik qat'iy
    hisoblanadi — 90-daqiqadagi 1:0 va 5-daqiqadagi 1:0 bir xil emas.
    """
    if status == "FT":
        if score_home > score_away:
            return {"home": 100, "draw": 0, "away": 0}
        if score_home < score_away:
            return {"home": 0, "draw": 0, "away": 100}
        return {"home": 0, "draw": 100, "away": 0}

    diff = score_home - score_away
    # 0.0 (o'yin boshi) -> 1.0 (o'yin oxiri): vaqt o'tgani sari ishonch ortadi
    progress = min(max(minute, 0), 90) / 90
    weight = GOAL_WEIGHT * (0.6 + 0.8 * progress)

    home = BASE_HOME + diff * weight
    away = BASE_AWAY - diff * weight
    # Hisob teng bo'lsa va vaqt oz qolgan bo'lsa — durang ehtimoli ortadi
    draw = BASE_DRAW + (12 * progress if diff == 0 else -abs(diff) * 4)

    values = {"home": home, "draw": draw, "away": away}
    # Manfiy yoki juda kichik qiymatlarni pastki chegaraga tortamiz
    clamped = {key: max(float(MIN_PERCENT), value) for key, value in values.items()}

    total = sum(clamped.values())
    percents = {key: int(round(value / total * 100)) for key, value in clamped.items()}

    # Yaxlitlashdan keyin yig'indi 99 yoki 101 bo'lishi mumkin — eng katta
    # ulushga tuzatma kiritamiz, natija har doim aniq 100 bo'ladi.
    drift = 100 - sum(percents.values())
    if drift:
        leader = max(percents, key=lambda key: percents[key])
        percents[leader] += drift

    return percents

"""Simulyatsiya rejimi uchun yangi o'yinlar yaratish.

Nima uchun kerak: ilgari bazaga faqat 3 ta o'yin bir marta yozilardi va ular
90-daqiqaga yetgach sayt abadiy muzlab qolardi — yangi o'yin paydo bo'lishining
hech qanday yo'li yo'q edi. Bu modul jadvalni to'ldirib turadi, shunda
API kaliti bo'lmasa ham platforma tirik ko'rinadi.
"""

import random
from datetime import timedelta
from typing import Dict, Iterable, List, Optional, Set

from app.core.clock import utcnow
from app.models.match import Match

# Simulyatsiya qilingan o'yinlar uchun ID diapazoni. API-Football'ning haqiqiy
# fixture ID'lari ~1-2 million atrofida, shuning uchun to'qnashuv bo'lmaydi.
SIMULATED_ID_START = 9_000_000

# Jadvalda doim shuncha bo'lajak o'yin turadi
UPCOMING_TARGET = 5


def _players(*names: str) -> List[str]:
    return list(names)


# Logotip URL'i ishonchli bo'lmagan jamoalarda bo'sh qoldirilgan — interfeys
# bunday holatda jamoa nomining bosh harflarini ko'rsatadi.
LEAGUE_CATALOG: List[Dict] = [
    {
        "id": 140,
        "name": "La Liga",
        "teams": [
            {
                "name": "Real Madrid",
                "logo": "https://media.api-sports.io/football/teams/541.png",
                "players": _players("Mbappe", "Vinicius Jr", "Bellingham", "Rodrygo", "Valverde"),
            },
            {
                "name": "Barcelona",
                "logo": "https://media.api-sports.io/football/teams/529.png",
                "players": _players("Lewandowski", "Yamal", "Raphinha", "Pedri", "Gundogan"),
            },
            {
                "name": "Atletico Madrid",
                "logo": "https://media.api-sports.io/football/teams/530.png",
                "players": _players("Griezmann", "Alvarez", "Sorloth", "Llorente", "De Paul"),
            },
            {
                "name": "Sevilla",
                "logo": "https://media.api-sports.io/football/teams/536.png",
                "players": _players("En-Nesyri", "Ocampos", "Rakitic", "Navas", "Gudelj"),
            },
        ],
    },
    {
        "id": 39,
        "name": "English Premier League",
        "teams": [
            {
                "name": "Arsenal",
                "logo": "https://media.api-sports.io/football/teams/42.png",
                "players": _players("Saka", "Havertz", "Martinelli", "Odegaard", "Rice"),
            },
            {
                "name": "Manchester City",
                "logo": "https://media.api-sports.io/football/teams/50.png",
                "players": _players("Haaland", "Foden", "De Bruyne", "Silva", "Kovacic"),
            },
            {
                "name": "Liverpool",
                "logo": "https://media.api-sports.io/football/teams/40.png",
                "players": _players("Salah", "Nunez", "Diaz", "Szoboszlai", "Mac Allister"),
            },
            {
                "name": "Chelsea",
                "logo": "https://media.api-sports.io/football/teams/49.png",
                "players": _players("Palmer", "Jackson", "Madueke", "Enzo", "Caicedo"),
            },
            {
                "name": "Manchester United",
                "logo": "https://media.api-sports.io/football/teams/33.png",
                "players": _players("Fernandes", "Rashford", "Hojlund", "Garnacho", "Mount"),
            },
            {
                "name": "Tottenham",
                "logo": "https://media.api-sports.io/football/teams/47.png",
                "players": _players("Son", "Maddison", "Kulusevski", "Johnson", "Sarr"),
            },
        ],
    },
    {
        "id": 1000,
        "name": "Uzbekistan Super League",
        "teams": [
            {
                "name": "Pakhtakor",
                "logo": "https://upload.wikimedia.org/wikipedia/en/e/e0/Pakhtakor_Tashkent_FK.png",
                "players": _players("Ceran", "Hamdamov", "Adhamzoda", "Usmonov", "Kholmatov"),
            },
            {
                "name": "Navbahor",
                "logo": "https://upload.wikimedia.org/wikipedia/uz/c/cf/Navbahor_namangan_logo.png",
                "players": _players("Turgunboev", "Tabatadze", "Boltaboev", "Jahongirov", "Iskanderov"),
            },
            # Quyidagi jamoalar uchun tasdiqlangan logotip va tarkib yo'q —
            # o'yinchilar raqam bilan ko'rsatiladi (to'qib chiqarilgan ism emas).
            {"name": "Nasaf", "logo": None, "players": []},
            {"name": "Bunyodkor", "logo": None, "players": []},
            {"name": "AGMK", "logo": None, "players": []},
            {"name": "Andijon", "logo": None, "players": []},
        ],
    },
]

GENERIC_PLAYERS = ["No. 9", "No. 10", "No. 7", "No. 11", "No. 8"]

# Tarkibdagi 11 ta o'rin uchun umumiy raqamlar
_GENERIC_LINEUP = [f"No. {n}" for n in range(1, 12)]


def _lineup_for(team: Dict) -> List[str]:
    """11 kishilik tarkib: ma'lum o'yinchilar + qolgan o'rinlar raqam bilan."""
    known = list(team.get("players") or [])
    filler = [name for name in _GENERIC_LINEUP if name not in known]
    return (known + filler)[:11]


def scorers_for(team_name: str) -> List[str]:
    """Gol muallifini tanlash uchun o'yinchilar ro'yxati."""
    for league in LEAGUE_CATALOG:
        for team in league["teams"]:
            if team["name"] == team_name and team.get("players"):
                return team["players"]
    return GENERIC_PLAYERS


def next_simulated_id(used_ids: Iterable[int]) -> int:
    """Simulyatsiya diapazonidagi keyingi bo'sh ID."""
    simulated = [i for i in used_ids if i >= SIMULATED_ID_START]
    return max(simulated) + 1 if simulated else SIMULATED_ID_START


def pair_key(home_name: str, away_name: str) -> frozenset:
    """Jamoalar juftligi — tartibdan qat'i nazar bir xil kalit."""
    return frozenset((home_name, away_name))


def build_fixture(
    match_id: int,
    kickoff_in_minutes: int,
    avoid_pairs: Optional[Set[frozenset]] = None,
) -> Match:
    """Tasodifiy liga va ikki jamoadan yangi (boshlanmagan) o'yin yasaydi.

    `avoid_pairs` — jadvalda allaqachon turgan juftliklar; bir xil bahs
    ketma-ket ikki marta chiqib qolmasligi uchun bir necha marta urinamiz.
    """
    avoid = avoid_pairs or set()

    league = random.choice(LEAGUE_CATALOG)
    home, away = random.sample(league["teams"], 2)

    for _ in range(10):
        if pair_key(home["name"], away["name"]) not in avoid:
            break
        league = random.choice(LEAGUE_CATALOG)
        home, away = random.sample(league["teams"], 2)

    return Match(
        id=match_id,
        league_id=league["id"],
        league_name=league["name"],
        home_team_name=home["name"],
        away_team_name=away["name"],
        home_team_logo=home["logo"],
        away_team_logo=away["logo"],
        status="NS",
        score_home=0,
        score_away=0,
        match_time=utcnow() + timedelta(minutes=kickoff_in_minutes),
        minute=0,
        lineups={"home": _lineup_for(home), "away": _lineup_for(away)},
        timeline=[],
        stats=None,  # statistika o'yin boshlangach paydo bo'ladi
        win_probability=None,
    )


def initial_stats() -> Dict:
    """O'yin boshlanganda qo'yiladigan boshlang'ich statistika."""
    return {
        "possession": {"home": 50, "away": 50},
        "shots": {"home": 0, "away": 0},
        "xG": {"home": 0.0, "away": 0.0},
    }

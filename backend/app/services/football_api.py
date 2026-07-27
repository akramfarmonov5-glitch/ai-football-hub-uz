import json
import urllib.request
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match import Match
from app.core.config import settings

# Simulyatsiya uchun jamoa o'yinchilari (real API kaliti bo'lmaganda ishlatiladi)
TEAM_PLAYERS = {
    "Real Madrid": ["Mbappe", "Vinicius Jr", "Bellingham", "Rodrygo", "Valverde"],
    "Barcelona": ["Lewandowski", "Yamal", "Raphinha", "Pedri", "Gundogan"],
    "Arsenal": ["Saka", "Havertz", "Martinelli", "Odegaard", "Rice"],
    "Manchester City": ["Haaland", "Foden", "De Bruyne", "Silva", "Kovacic"],
    "Pakhtakor": ["Ceran", "Hamdamov", "Adhamzoda", "Usmonov", "Kholmatov"],
    "Navbahor": ["Turgunboev", "Tabatadze", "Boltaboev", "Jahongirov", "Iskanderov"],
}

# Har qanday jamoa uchun umumiy zaxira o'yinchi nomlari
GENERIC_PLAYERS = ["No. 9", "No. 10", "No. 7", "No. 11", "No. 8"]


def get_players_for_team(team_name: str) -> list[str]:
    """Berilgan jamoa uchun o'yinchilar ro'yxatini qaytaradi (gol muallifini tanlash uchun)."""
    return TEAM_PLAYERS.get(team_name, GENERIC_PLAYERS)


class FootballAPIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.API_FOOTBALL_KEY
        self.base_url = "https://v3.football.api-sports.io"

    async def fetch_and_update_real_matches(self):
        """
        Fetches real matches from API-Football if API key is provided in .env,
        otherwise falls back to simulation mode.
        """
        if not self.api_key or self.api_key == "":
            print("API_FOOTBALL_KEY is not configured in .env. Running in simulated match mode.")
            return await self.simulate_live_updates()

        headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": self.api_key
        }

        # Fetch live matches first
        try:
            req = urllib.request.Request(f"{self.base_url}/fixtures?live=all", headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            if "response" in data:
                fixtures = data["response"]
                for f in fixtures:
                    fixture_id = f["fixture"]["id"]
                    league = f["league"]
                    teams = f["teams"]
                    goals = f["goals"]
                    status = f["fixture"]["status"]
                    
                    # Check if match exists in DB
                    db_match = await self.db.get(Match, fixture_id)
                    if not db_match:
                        db_match = Match(id=fixture_id)

                    db_match.league_id = league["id"]
                    db_match.league_name = league["name"]
                    db_match.home_team_name = teams["home"]["name"]
                    db_match.away_team_name = teams["away"]["name"]
                    db_match.home_team_logo = teams["home"]["logo"]
                    db_match.away_team_logo = teams["away"]["logo"]
                    db_match.status = "LIVE" if status["short"] in ["1H", "2H", "HT"] else status["short"]
                    db_match.score_home = goals["home"] or 0
                    db_match.score_away = goals["away"] or 0
                    db_match.match_time = datetime.fromisoformat(f["fixture"]["date"].replace("Z", "+00:00"))
                    db_match.minute = status["elapsed"] or 0
                    
                    # Update stats if available
                    db_match.stats = {
                        "possession": {"home": 50, "away": 50}, # API-Football requires secondary call for stats, mock defaults or handle gracefully
                        "shots": {"home": 0, "away": 0},
                        "xG": {"home": 0, "away": 0}
                    }
                    
                    # Estimate win probability dynamically
                    diff = db_match.score_home - db_match.score_away
                    prob = {"home": 33, "draw": 34, "away": 33}
                    if diff > 0:
                        prob = {"home": 50 + diff * 15, "draw": max(10, 30 - diff * 10), "away": max(5, 20 - diff * 5)}
                    elif diff < 0:
                        prob = {"home": max(5, 20 - abs(diff) * 5), "draw": max(10, 30 - abs(diff) * 10), "away": 50 + abs(diff) * 15}
                    db_match.win_probability = prob

                    self.db.add(db_match)
                
                await self.db.commit()
                print(f"Successfully updated {len(fixtures)} live matches from API-Football.")
                result = await self.db.execute(select(Match).where(Match.status == "LIVE"))
                return result.scalars().all()

        except Exception as e:
            print(f"Error fetching live matches from API-Football: {e}")
            return await self.simulate_live_updates()

    async def simulate_live_updates(self):
        """
        Fallback simulation engine if API key is not configured.
        """
        # (Keep the existing simulation code operational)
        import random

        result = await self.db.execute(select(Match).where(Match.status == "LIVE"))
        live_matches = result.scalars().all()
        updated_matches = []

        for match in live_matches:
            match.minute = (match.minute or 0) + 1
            if match.minute >= 90:
                match.status = "FT"
            else:
                chance = random.random()
                if match.stats and "possession" in match.stats:
                    pos = match.stats["possession"]
                    delta = random.choice([-2, -1, 1, 2])
                    new_home = min(max(pos["home"] + delta, 30), 70)
                    match.stats = {
                        "possession": {"home": new_home, "away": 100 - new_home},
                        "shots": {
                            "home": match.stats["shots"]["home"] + (1 if random.random() > 0.85 else 0),
                            "away": match.stats["shots"]["away"] + (1 if random.random() > 0.85 else 0)
                        },
                        "xG": {
                            "home": round(match.stats["xG"]["home"] + (random.uniform(0.02, 0.15) if random.random() > 0.9 else 0), 2),
                            "away": round(match.stats["xG"]["away"] + (random.uniform(0.02, 0.15) if random.random() > 0.9 else 0), 2)
                        }
                    }

                if chance < 0.025:
                    team = "home" if random.random() > 0.5 else "away"
                    team_name = match.home_team_name if team == "home" else match.away_team_name
                    players = get_players_for_team(team_name)
                    scorer = random.choice(players)
                    
                    if team == "home":
                        match.score_home += 1
                    else:
                        match.score_away += 1

                    timeline = list(match.timeline or [])
                    timeline.append({
                        "time": match.minute,
                        "type": "Goal",
                        "detail": f"{scorer} (Gol!)",
                        "team": team
                    })
                    match.timeline = timeline
                    
                    diff = match.score_home - match.score_away
                    if diff > 0:
                        match.win_probability = {"home": 60 + diff * 10, "draw": 25 - diff * 5, "away": 15 - diff * 5}
                    elif diff < 0:
                        match.win_probability = {"home": 15 + diff * 5, "draw": 25 + diff * 5, "away": 60 - diff * 10}
                    else:
                        match.win_probability = {"home": 35, "draw": 30, "away": 35}

            self.db.add(match)
            updated_matches.append(match)

        await self.db.commit()
        return updated_matches

    async def seed_mock_matches_if_empty(self):
        # Keeps initial seeds intact so the workspace has instant matches
        count = await self.db.scalar(select(func.count()).select_from(Match))
        if count and count > 0:
            return

        now = datetime.utcnow()
        mock_matches = [
            Match(
                id=2001,
                league_id=140,
                league_name="La Liga",
                home_team_name="Real Madrid",
                away_team_name="Barcelona",
                home_team_logo="https://media.api-sports.io/football/teams/541.png",
                away_team_logo="https://media.api-sports.io/football/teams/529.png",
                status="FT",
                score_home=3,
                score_away=2,
                match_time=now - timedelta(hours=3),
                minute=90,
                lineups={
                    "home": ["Courtois", "Carvajal", "Militao", "Rudiger", "Mendy", "Valverde", "Tchouameni", "Bellingham", "Rodrygo", "Mbappe", "Vinicius Jr"],
                    "away": ["Ter Stegen", "Kounde", "Araujo", "Cubarsi", "Balde", "Pedri", "Gundogan", "De Jong", "Yamal", "Lewandowski", "Raphinha"]
                },
                timeline=[
                    {"time": 12, "type": "Goal", "detail": "Lewandowski (Assist: Yamal)", "team": "away"},
                    {"time": 32, "type": "Goal", "detail": "Mbappe (Penalty)", "team": "home"},
                    {"time": 58, "type": "Goal", "detail": "Vinicius Jr", "team": "home"},
                    {"time": 76, "type": "Goal", "detail": "Raphinha", "team": "away"},
                    {"time": 89, "type": "Goal", "detail": "Bellingham (Assist: Vinicius Jr)", "team": "home"},
                ],
                stats={"possession": {"home": 52, "away": 48}, "shots": {"home": 16, "away": 12}, "xG": {"home": 2.1, "away": 1.7}},
                win_probability={"home": 100, "draw": 0, "away": 0},
                ai_preview="El Clasico o'yinida shiddatli to'qnashuv kutilmoqda. Ikkala jamoa ham hujumkor futbol tarafdori.",
                ai_analysis="Ajoyib va gollarga boy El Clasico guvohi bo'ldik. Jude Bellingham so'nggi daqiqalarda g'alaba golini kiritdi."
            ),
            Match(
                id=2002,
                league_id=39,
                league_name="English Premier League",
                home_team_name="Arsenal",
                away_team_name="Manchester City",
                home_team_logo="https://media.api-sports.io/football/teams/42.png",
                away_team_logo="https://media.api-sports.io/football/teams/50.png",
                status="LIVE",
                score_home=1,
                score_away=1,
                match_time=now - timedelta(minutes=42),
                minute=42,
                lineups={
                    "home": ["Raya", "White", "Saliba", "Gabriel", "Timber", "Odegaard", "Partey", "Rice", "Saka", "Havertz", "Martinelli"],
                    "away": ["Ederson", "Walker", "Dias", "Akanji", "Gvardiol", "Rodri", "Kovacic", "De Bruyne", "Foden", "Silva", "Haaland"]
                },
                timeline=[
                    {"time": 18, "type": "Goal", "detail": "Haaland (Assist: De Bruyne)", "team": "away"},
                    {"time": 35, "type": "Goal", "detail": "Saka (Assist: Odegaard)", "team": "home"}
                ],
                stats={"possession": {"home": 45, "away": 55}, "shots": {"home": 5, "away": 8}, "xG": {"home": 0.8, "away": 1.1}},
                win_probability={"home": 33, "draw": 35, "away": 32},
                ai_preview="Chempionlik uchun kurashadigan ikki gigant to'qnashuvi. Arsenal o'z maydonida ochko yo'qotmaslikka harakat qiladi."
            ),
            Match(
                id=2003,
                league_id=1000,
                league_name="Uzbekistan Super League",
                home_team_name="Pakhtakor",
                away_team_name="Navbahor",
                home_team_logo="https://upload.wikimedia.org/wikipedia/en/e/e0/Pakhtakor_Tashkent_FK.png",
                away_team_logo="https://upload.wikimedia.org/wikipedia/uz/c/cf/Navbahor_namangan_logo.png",
                status="LIVE",
                score_home=0,
                score_away=0,
                match_time=now - timedelta(minutes=15),
                minute=15,
                lineups={
                    "home": ["Nazarov", "Saiyodv", "Alijonov", "Hamraliev", "Azmiddinov", "Sobirkhodjaev", "Kholmatov", "Hamdamov", "Ceran", "Adhamzoda", "Usmonov"],
                    "away": ["Yusupov", "Golban", "Ivanovic", "Milovic", "Sayfiev", "Ismailov", "Iskanderov", "Boltaboev", "Turgunboev", "Tabatadze", "Jahongirov"]
                },
                timeline=[],
                stats={"possession": {"home": 50, "away": 50}, "shots": {"home": 2, "away": 1}, "xG": {"home": 0.15, "away": 0.08}},
                win_probability={"home": 40, "draw": 35, "away": 25},
                ai_preview="O'zbekiston derbisi deb ataluvchi ushbu bahsda murosasiz kurash kechishi kutilmoqda."
            )
        ]
        self.db.add_all(mock_matches)
        await self.db.commit()

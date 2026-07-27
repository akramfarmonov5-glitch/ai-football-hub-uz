"""TheSportsDB — haqiqiy o'yin ma'lumotlari.

Nima uchun aynan shu manba: bepul kalitida **O'zbekiston Superligasi** bor
(4794), boshqa bepul xizmatlarda (masalan football-data.org) faqat yirik
Yevropa ligalari mavjud. Sayt O'zbekiston auditoriyasi uchun bo'lgani sababli
bu hal qiluvchi jihat.

Bepul tarif cheklovi: **jonli (daqiqama-daqiqa) hisob yo'q**. Shuning uchun
o'yinlar faqat ikki holatda bo'ladi — boshlanmagan (NS) yoki tugagan (FT).
Soxta "jonli daqiqa" ko'rsatilmaydi.

Ishlatiladigan endpointlar (ikkalasi ham bepul kalitda tekshirilgan):
  * eventsday.php   — kun bo'yicha o'yinlar (jadval va natijalar)
  * lookuptable.php — rasmiy turnir jadvali (shu jumladan "forma")
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import to_naive_utc, utcnow
from app.core.config import settings
from app.models.match import Match

logger = logging.getLogger(__name__)

BASE_URL = "https://www.thesportsdb.com/api/v1/json"

# TheSportsDB holatlarini loyihadagi holatlarga o'girish
FINISHED_STATUSES = {"FT", "AET", "PEN", "Match Finished", "AP"}
LIVE_STATUSES = {"1H", "2H", "HT", "ET", "BT", "P", "LIVE"}

# Liga mavsumi ("2026" yoki "2026-2027") — jarayon davomida saqlanadi,
# u tez-tez o'zgarmaydi va har so'rovda qayta so'rash isrofgarchilik bo'lardi.
_season_cache: Dict[int, str] = {}


class SportsDBService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.SPORTSDB_API_KEY or "3"
        self.leagues = settings.sportsdb_league_ids

    @property
    def enabled(self) -> bool:
        return settings.SPORTSDB_ENABLED and bool(self.leagues)

    def _url(self, path: str) -> str:
        return f"{BASE_URL}/{self.api_key}/{path}"

    async def _get(self, client: httpx.AsyncClient, path: str) -> Dict[str, Any]:
        try:
            response = await client.get(self._url(path))
            response.raise_for_status()
            return response.json() or {}
        except Exception as exc:
            logger.warning("TheSportsDB so'rovi muvaffaqiyatsiz (%s): %s", path, exc)
            return {}

    async def _current_season(self, client: httpx.AsyncClient, league_id: int) -> Optional[str]:
        if league_id in _season_cache:
            return _season_cache[league_id]

        data = await self._get(client, f"lookupleague.php?id={league_id}")
        leagues = data.get("leagues") or []
        if not leagues:
            return None

        season = leagues[0].get("strCurrentSeason")
        if season:
            _season_cache[league_id] = season
        return season

    # ------------------------------------------------------------------
    # O'yinlar
    # ------------------------------------------------------------------
    @staticmethod
    def _map_status(raw: Optional[str], has_score: bool) -> str:
        status = (raw or "").strip()
        if status in FINISHED_STATUSES:
            return "FT"
        if status in LIVE_STATUSES:
            return "LIVE"
        # Ba'zi yozuvlarda status bo'sh, lekin hisob bor — bu tugagan o'yin
        return "FT" if has_score else "NS"

    def _to_match(self, event: Dict[str, Any]) -> Optional[Match]:
        try:
            match_id = int(event["idEvent"])
        except (KeyError, TypeError, ValueError):
            return None

        if (event.get("strPostponed") or "no").lower() == "yes":
            return None  # qoldirilgan o'yin jadvalda chalkashlik keltiradi

        home_score = event.get("intHomeScore")
        away_score = event.get("intAwayScore")
        has_score = home_score is not None and away_score is not None

        # strTimestamp — UTC (strTimeLocal alohida maydonda beriladi)
        timestamp = event.get("strTimestamp")
        if timestamp:
            kickoff = to_naive_utc(datetime.fromisoformat(timestamp.replace("Z", "+00:00")))
        elif event.get("dateEvent"):
            kickoff = datetime.fromisoformat(
                f"{event['dateEvent']}T{event.get('strTime') or '00:00:00'}"
            )
        else:
            return None

        return Match(
            id=match_id,
            league_id=int(event.get("idLeague") or 0),
            league_name=event.get("strLeague") or "",
            home_team_name=event.get("strHomeTeam") or "",
            away_team_name=event.get("strAwayTeam") or "",
            home_team_logo=event.get("strHomeTeamBadge"),
            away_team_logo=event.get("strAwayTeamBadge"),
            status=self._map_status(event.get("strStatus"), has_score),
            score_home=int(home_score) if has_score else 0,
            score_away=int(away_score) if has_score else 0,
            match_time=kickoff,
            minute=0,
        )

    async def sync_matches(self, window_days: int = 1) -> List[Match]:
        """Kecha/bugun/ertangi o'yinlarni bazaga yozadi.

        `eventsday.php` bepul kalitda kunlik to'liq ro'yxatni beradi
        (`eventspastleague` esa atigi bitta o'yin qaytaradi).
        """
        if not self.enabled:
            return []

        today = utcnow().date()
        days = [today + timedelta(days=offset) for offset in range(-window_days, window_days + 1)]

        updated: List[Match] = []
        async with httpx.AsyncClient(timeout=20.0) as client:
            for league_id in self.leagues:
                for day in days:
                    data = await self._get(
                        client, f"eventsday.php?d={day}&s=Soccer&l={league_id}"
                    )
                    for event in data.get("events") or []:
                        fresh = self._to_match(event)
                        if fresh is None:
                            continue

                        existing = await self.db.get(Match, fresh.id)
                        if existing is None:
                            self.db.add(fresh)
                            updated.append(fresh)
                            continue

                        # Faqat o'zgargan bo'lsa yangilaymiz — WebSocket'ga
                        # keraksiz xabar ketmasligi uchun
                        changed = (
                            existing.status != fresh.status
                            or existing.score_home != fresh.score_home
                            or existing.score_away != fresh.score_away
                            or existing.match_time != fresh.match_time
                        )
                        existing.league_name = fresh.league_name
                        existing.home_team_logo = fresh.home_team_logo
                        existing.away_team_logo = fresh.away_team_logo
                        existing.status = fresh.status
                        existing.score_home = fresh.score_home
                        existing.score_away = fresh.score_away
                        existing.match_time = fresh.match_time
                        self.db.add(existing)
                        if changed:
                            updated.append(existing)

        await self.db.commit()
        if updated:
            logger.info("TheSportsDB: %d ta o'yin yangilandi", len(updated))
        return updated

    # ------------------------------------------------------------------
    # Turnir jadvali
    # ------------------------------------------------------------------
    async def fetch_standings(self) -> List[dict]:
        """Rasmiy turnir jadvali.

        O'yinlardan hisoblab bo'lmaydi: bepul tarifda faqat bir necha kunlik
        o'yinlar olinadi, mavsum boshidan beri hamma natija yo'q. Shu sababli
        jadval to'g'ridan-to'g'ri manbadan olinadi.
        """
        if not self.enabled:
            return []

        tables: List[dict] = []
        async with httpx.AsyncClient(timeout=20.0) as client:
            for league_id in self.leagues:
                season = await self._current_season(client, league_id)
                if not season:
                    continue

                data = await self._get(client, f"lookuptable.php?l={league_id}&s={season}")
                rows = data.get("table") or []
                if not rows:
                    continue

                table = [self._to_standing_row(row) for row in rows]

                # Mavsum hali boshlanmagan bo'lsa jadval butunlay nolga to'la
                # bo'ladi (yozda Yevropa ligalarida shunday). Bunday jadvalni
                # ko'rsatishdan ma'no yo'q — liga o'tkazib yuboriladi.
                if all(row["played"] == 0 for row in table):
                    logger.info(
                        "Liga %s: %s mavsumi hali boshlanmagan, jadval ko'rsatilmaydi",
                        league_id,
                        season,
                    )
                    continue

                tables.append(
                    {
                        "league_id": league_id,
                        "league_name": rows[0].get("strLeague") or "",
                        "table": table,
                    }
                )

        tables.sort(key=lambda table: table["league_name"])
        return tables

    @staticmethod
    def _to_standing_row(row: Dict[str, Any]) -> dict:
        def num(key: str) -> int:
            try:
                return int(row.get(key) or 0)
            except (TypeError, ValueError):
                return 0

        # strForm "WWDWW" ko'rinishida; eng yangi natija oxirida turishi uchun
        # loyiha kelishuviga moslaymiz
        form = [ch for ch in (row.get("strForm") or "") if ch in "WDL"][-5:]

        return {
            "position": num("intRank"),
            "team": row.get("strTeam") or "",
            "logo": row.get("strBadge"),
            "played": num("intPlayed"),
            "won": num("intWin"),
            "drawn": num("intDraw"),
            "lost": num("intLoss"),
            "goals_for": num("intGoalsFor"),
            "goals_against": num("intGoalsAgainst"),
            "goal_difference": num("intGoalDifference"),
            "points": num("intPoints"),
            "form": form,
        }

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

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clock import to_naive_utc, utcnow
from app.core.config import settings
from app.models.match import Match
from app.models.team import Team
from app.services.teams import team_slug

logger = logging.getLogger(__name__)

BASE_URL = "https://www.thesportsdb.com/api/v1/json"

# TheSportsDB holatlarini loyihadagi holatlarga o'girish
FINISHED_STATUSES = {"FT", "AET", "PEN", "Match Finished", "AP"}
LIVE_STATUSES = {"1H", "2H", "HT", "ET", "BT", "P", "LIVE"}

# Liga mavsumi ("2026" yoki "2026-2027") — jarayon davomida saqlanadi,
# u tez-tez o'zgarmaydi va har so'rovda qayta so'rash isrofgarchilik bo'lardi.
_season_cache: Dict[int, str] = {}

# So'rovlar orasidagi eng kichik tanaffus. Bepul tarif daqiqasiga 30 ta
# so'rovga ruxsat beradi; har liga uchun alohida so'rov ketgani sababli
# 8 ta liga bilan bitta sinxronizatsiya 30 tadan oshib ketishi mumkin edi.
# (Ligasiz `eventsday.php` bepul kalitda atigi 3 ta o'yin qaytaradi, ya'ni
# so'rovlarni birlashtirib bo'lmaydi.)
_last_request_at: float = 0.0
_request_lock = asyncio.Lock()

# Turnir jadvali keshi. Busiz /standings/ so'rovi 8 ta liga uchun o'nlab
# so'rov qilardi va tanaffuslar bilan birga bir daqiqagacha cho'zilardi —
# sahifa umuman ochilmasdi. Jadval faqat o'yin tugagandan keyin o'zgaradi,
# shuning uchun uni keshlash mutlaqo o'rinli.
_standings_cache: Optional[List[dict]] = None
_standings_cached_at: float = 0.0
_standings_lock = asyncio.Lock()


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

    async def _throttle(self) -> None:
        """So'rovlar orasida eng kichik tanaffusni ta'minlaydi."""
        global _last_request_at

        interval = settings.SPORTSDB_REQUEST_INTERVAL_MS / 1000
        if interval <= 0:
            return

        async with _request_lock:
            kutish = interval - (time.monotonic() - _last_request_at)
            if kutish > 0:
                await asyncio.sleep(kutish)
            _last_request_at = time.monotonic()

    async def _get(self, client: httpx.AsyncClient, path: str) -> Dict[str, Any]:
        await self._throttle()
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
    # Jamoa profillari
    # ------------------------------------------------------------------
    async def sync_team_profiles(self, limit: int = 8) -> List[Team]:
        """O'yinlarda uchragan, lekin profili hali yo'q jamoalarni yuklaydi.

        `lookup_all_teams.php` bepul kalitda liga ID'sini e'tiborsiz qoldiradi
        (qaysi liga so'ralmasin, bir xil 24 ta ingliz jamoasini qaytaradi —
        tekshirilgan), shuning uchun har jamoa nomi bo'yicha alohida
        qidiriladi. Profil deyarli o'zgarmaydi, shuning uchun bir marta
        olinadi va bazada qoladi.

        Har qadamda bir nechtasi olinadi — so'rovlar limitini yemasligi uchun.
        """
        if not self.enabled:
            return []

        mavjud = set((await self.db.execute(select(Team.name))).scalars().all())

        # O'yinlardagi barcha jamoa nomlari (liga ID'si bilan birga)
        rows = await self.db.execute(
            select(Match.home_team_name, Match.league_id).union(
                select(Match.away_team_name, Match.league_id)
            )
        )
        kerakli = [(nom, liga) for nom, liga in rows.all() if nom and nom not in mavjud]
        if not kerakli:
            return []

        yaratilgan: List[Team] = []
        async with httpx.AsyncClient(timeout=20.0) as client:
            for nom, league_id in kerakli[:limit]:
                team = await self._fetch_team(client, nom, league_id)
                if team is None:
                    continue
                # Bir jamoa ikki liga ostida uchrashi mumkin (masalan
                # Chempionlar ligasi + milliy chempionat) — ID bo'yicha tekshiramiz
                if await self.db.get(Team, team.id):
                    continue
                self.db.add(team)
                yaratilgan.append(team)

        if yaratilgan:
            await self.db.commit()
            logger.info("%d ta jamoa profili yuklandi", len(yaratilgan))
        return yaratilgan

    async def _fetch_team(
        self, client: httpx.AsyncClient, name: str, league_id: Optional[int]
    ) -> Optional[Team]:
        data = await self._get(client, f"searchteams.php?t={quote(name)}")
        results = data.get("teams") or []
        if not results:
            logger.info("Jamoa topilmadi: %s", name)
            return None

        # Bir nomda bir nechta klub bo'lishi mumkin — ligasi mos kelganini olamiz
        chosen = results[0]
        if league_id:
            for item in results:
                try:
                    if int(item.get("idLeague") or 0) == league_id:
                        chosen = item
                        break
                except (TypeError, ValueError):
                    continue

        try:
            team_id = int(chosen["idTeam"])
        except (KeyError, TypeError, ValueError):
            return None

        def son(key: str) -> Optional[int]:
            try:
                qiymat = int(chosen.get(key) or 0)
                return qiymat or None
            except (TypeError, ValueError):
                return None

        # Liga jamoaning O'Z chempionatidan olinadi, o'yin ligasidan emas:
        # Chempionlar ligasidagi o'yin uchun `league_id` 4480 bo'lardi-yu,
        # `league_name` "Danish Superliga" bo'lib qolardi. Turnir jadvalidagi
        # o'rni ham jamoaning milliy chempionatida qidirilishi kerak.
        own_league = son("idLeague") or league_id

        return Team(
            id=team_id,
            # Slug o'yinlardagi nomdan yasaladi — havolalar shu nom bilan quriladi
            slug=team_slug(name),
            name=name,
            league_id=own_league,
            league_name=chosen.get("strLeague"),
            badge=chosen.get("strBadge"),
            stadium=chosen.get("strStadium"),
            stadium_capacity=son("intStadiumCapacity"),
            location=chosen.get("strLocation"),
            country=chosen.get("strCountry"),
            founded=son("intFormedYear"),
            website=chosen.get("strWebsite"),
            description=chosen.get("strDescriptionEN"),
        )

    # ------------------------------------------------------------------
    # Turnir jadvali
    # ------------------------------------------------------------------
    async def fetch_standings(self, force: bool = False) -> List[dict]:
        """Rasmiy turnir jadvali (keshlangan).

        O'yinlardan hisoblab bo'lmaydi: bepul tarifda faqat bir necha kunlik
        o'yinlar olinadi, mavsum boshidan beri hamma natija yo'q. Shu sababli
        jadval to'g'ridan-to'g'ri manbadan olinadi.

        Har liga uchun ikkitagacha so'rov ketadi va ular orasida tanaffus bor,
        ya'ni to'liq yangilash bir daqiqagacha cho'zilishi mumkin. Shuning
        uchun natija keshlanadi va fon vazifasi uni oldindan to'ldirib turadi —
        foydalanuvchi hech qachon kutmaydi.
        """
        global _standings_cache, _standings_cached_at

        if not self.enabled:
            return []

        ttl = settings.SPORTSDB_POLL_SECONDS
        if not force and _standings_cache is not None:
            if time.monotonic() - _standings_cached_at < ttl:
                return _standings_cache

        async with _standings_lock:
            # Kutib turgan paytda boshqa so'rov keshni yangilagan bo'lishi mumkin
            if not force and _standings_cache is not None:
                if time.monotonic() - _standings_cached_at < ttl:
                    return _standings_cache

            tables = await self._fetch_standings_uncached()

            # Bo'sh natija keshlanmaydi: tarmoq nosozligi tufayli jadval
            # butun TTL davomida yo'qolib turmasligi kerak
            if tables:
                _standings_cache = tables
                _standings_cached_at = time.monotonic()
            elif _standings_cache is not None:
                logger.warning("Jadval yangilanmadi — eski keshdagi ma'lumot beriladi")
                return _standings_cache

            return tables

    async def _fetch_standings_uncached(self) -> List[dict]:
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

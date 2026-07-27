"""Turnir jadvalini hisoblash.

Jadval alohida saqlanmaydi — har safar tugagan o'yinlardan qayta hisoblanadi.
Shu sababli u hech qachon o'yin natijalari bilan nomuvofiq bo'lib qolmaydi:
admin hisobni tuzatsa ham, o'yin qayta hisoblansa ham jadval o'zi yangilanadi.

Saralash qoidasi (UEFA/FIFA odatiy tartibi):
  1. ochko
  2. gollar farqi
  3. urilgan gollar
  4. jamoa nomi (alifbo — natija barqaror bo'lishi uchun)
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match

logger = logging.getLogger(__name__)

WIN_POINTS = 3
DRAW_POINTS = 1

# "Forma" ustunida ko'rsatiladigan oxirgi o'yinlar soni
FORM_LENGTH = 5


@dataclass
class TeamRow:
    """Bitta jamoaning jadvaldagi qatori."""

    team: str
    logo: Optional[str] = None
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    # Eng yangi natija oxirida turadi
    form: List[str] = field(default_factory=list)

    @property
    def points(self) -> int:
        return self.won * WIN_POINTS + self.drawn * DRAW_POINTS

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def add_result(self, scored: int, conceded: int, logo: Optional[str]) -> None:
        self.played += 1
        self.goals_for += scored
        self.goals_against += conceded

        if scored > conceded:
            self.won += 1
            self.form.append("W")
        elif scored < conceded:
            self.lost += 1
            self.form.append("L")
        else:
            self.drawn += 1
            self.form.append("D")

        # Logotip keyinroq paydo bo'lishi mumkin (masalan real API'dan)
        if logo and not self.logo:
            self.logo = logo


def _sort_key(row: TeamRow):
    """Ochko -> gollar farqi -> urilgan gollar -> nom (barqaror tartib uchun)."""
    return (-row.points, -row.goal_difference, -row.goals_for, row.team)


def build_tables(matches: Iterable[Match]) -> List[dict]:
    """Tugagan o'yinlardan har bir liga uchun jadval yasaydi.

    O'yinlar vaqt bo'yicha o'sish tartibida kelishi kutiladi — "forma"
    ustuni to'g'ri tartibda to'lishi uchun.
    """
    leagues: Dict[int, dict] = {}

    for match in matches:
        if match.status != "FT":
            continue
        if match.score_home is None or match.score_away is None:
            continue

        league = leagues.setdefault(
            match.league_id,
            {"league_id": match.league_id, "league_name": match.league_name, "rows": {}},
        )
        rows: Dict[str, TeamRow] = league["rows"]

        home = rows.setdefault(match.home_team_name, TeamRow(team=match.home_team_name))
        away = rows.setdefault(match.away_team_name, TeamRow(team=match.away_team_name))

        home.add_result(match.score_home, match.score_away, match.home_team_logo)
        away.add_result(match.score_away, match.score_home, match.away_team_logo)

    tables: List[dict] = []
    for league in leagues.values():
        ordered = sorted(league["rows"].values(), key=_sort_key)
        tables.append(
            {
                "league_id": league["league_id"],
                "league_name": league["league_name"],
                "table": [
                    {
                        "position": index,
                        "team": row.team,
                        "logo": row.logo,
                        "played": row.played,
                        "won": row.won,
                        "drawn": row.drawn,
                        "lost": row.lost,
                        "goals_for": row.goals_for,
                        "goals_against": row.goals_against,
                        "goal_difference": row.goal_difference,
                        "points": row.points,
                        # Oxirgi N o'yin, eng yangisi oxirida
                        "form": row.form[-FORM_LENGTH:],
                    }
                    for index, row in enumerate(ordered, start=1)
                ],
            }
        )

    # Ligalar nomi bo'yicha tartiblanadi — sahifa har safar bir xil ko'rinsin
    tables.sort(key=lambda table: table["league_name"])
    return tables


async def get_standings(
    db: AsyncSession, league_id: Optional[int] = None
) -> List[dict]:
    """Turnir jadvali.

    Ikki manba:
      * **TheSportsDB** — rasmiy jadval. Haqiqiy rejimda o'yinlardan hisoblab
        bo'lmaydi: bepul tarifda faqat bir necha kunlik o'yinlar olinadi,
        mavsum boshidan beri hamma natija bazada yo'q.
      * **Bazadagi o'yinlar** — simulyatsiya rejimida (barcha natijalar
        o'zimizda bo'lgani uchun jadval to'liq hisoblanadi).
    """
    from app.services.sportsdb import SportsDBService  # aylanma importni oldini olish

    sportsdb = SportsDBService(db)
    if sportsdb.enabled:
        tables = await sportsdb.fetch_standings()
        if tables:
            if league_id is not None:
                tables = [t for t in tables if t["league_id"] == league_id]
            return tables
        logger.warning("TheSportsDB jadvali bo'sh — o'yinlardan hisoblanadi")

    query = select(Match).where(Match.status == "FT").order_by(Match.match_time.asc())
    if league_id is not None:
        query = query.where(Match.league_id == league_id)

    result = await db.execute(query)
    return build_tables(result.scalars().all())

"""Jamoa sahifasi uchun ma'lumot yig'ish.

Sahifa mazmuni bazadagi ma'lumotdan quriladi — profil (`teams` jadvali),
o'yinlar (`matches`) va turnir jadvalidagi qatori. Shu sababli sahifa
ochilganda tashqi API ga so'rov ketmaydi.
"""

import re
import unicodedata
from typing import Dict, List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match
from app.models.team import Team

# Sahifada ko'rsatiladigan o'yinlar soni
RECENT_LIMIT = 8
UPCOMING_LIMIT = 5

# O'zbekcha apostroflarni olib tashlaymiz: "Mash'al" -> "mashal"
_APOSTROPHES = str.maketrans({"'": "", "’": "", "‘": "", "`": "", "ʻ": "", "ʼ": ""})

# Unicode normalizatsiyasi ajratmaydigan harflar (ular alohida kod nuqtalari):
# ł, ø, đ, ß, æ, œ. Busiz "Górnik" -> "grnik" kabi buzuq slug chiqardi.
_SPECIAL = str.maketrans(
    {"ł": "l", "ø": "o", "đ": "d", "ð": "d", "þ": "th", "ß": "ss", "æ": "ae", "œ": "oe"}
)


def team_slug(name: str) -> str:
    """Jamoa nomidan URL uchun barqaror slug.

    Barqarorligi muhim: havolalar shu asosda quriladi, o'zgarsa eski
    manzillar ishlamay qoladi.

    Diakritik belgilar tashlab yuborilmaydi, balki lotin ekvivalentiga
    o'giriladi: "Fenerbahçe" -> "fenerbahce", "Atlético" -> "atletico".

    DIQQAT: frontenddagi `lib/teamSlug.ts` bilan aynan bir xil ishlashi
    shart — havolalar o'sha yerda quriladi.
    """
    text = (name or "").lower().translate(_APOSTROPHES).translate(_SPECIAL)
    # NFKD urg'uli harfni "harf + belgi" ga ajratadi, keyin belgilarni olib
    # tashlaymiz: ó -> o, ç -> c, é -> e
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:80].strip("-") or "jamoa"


async def list_teams(db: AsyncSession) -> List[dict]:
    """Profili mavjud jamoalar ro'yxati (sitemap va indeks uchun)."""
    result = await db.execute(select(Team).order_by(Team.name.asc()))
    return [
        {
            "slug": team.slug,
            "name": team.name,
            "badge": team.badge,
            "league_name": team.league_name,
        }
        for team in result.scalars().all()
    ]


async def get_team_page(db: AsyncSession, slug: str) -> Optional[dict]:
    """Jamoa sahifasi uchun to'liq ma'lumot. Topilmasa None.

    Profil (`teams` jadvali) bosqichma-bosqich to'ldiriladi, lekin sahifa
    profilsiz ham ishlashi shart: turnir jadvali va o'yin kartalari barcha
    jamoalarni havola qiladi, profili hali yuklanmagani bosilsa 404 chiqardi.
    Shu sababli profil bo'lmasa sahifa o'yinlardan quriladi.
    """
    team = await db.scalar(select(Team).where(Team.slug == slug))

    if team is not None:
        name = team.name
        profil = {
            "badge": team.badge,
            "league_id": team.league_id,
            "league_name": team.league_name,
            "stadium": team.stadium,
            "stadium_capacity": team.stadium_capacity,
            "location": team.location,
            "country": team.country,
            "founded": team.founded,
            "website": team.website,
            "description": team.description,
        }
    else:
        topilgan = await _resolve_name_from_matches(db, slug)
        if topilgan is None:
            return None
        name, league_id, league_name, badge = topilgan
        profil = {
            "badge": badge,
            "league_id": league_id,
            "league_name": league_name,
            "stadium": None,
            "stadium_capacity": None,
            "location": None,
            "country": None,
            "founded": None,
            "website": None,
            "description": None,
        }

    matches = await _team_matches(db, name)

    return {
        "slug": slug,
        "name": name,
        **profil,
        "recent_matches": matches["recent"],
        "upcoming_matches": matches["upcoming"],
        "standing": await _standing_row_for(db, name, slug, profil["league_id"]),
    }


async def _resolve_name_from_matches(db: AsyncSession, slug: str):
    """Slug bo'yicha jamoa nomini o'yinlardan topadi.

    Qaytaradi: (nom, league_id, league_name, gerb) yoki None.
    """
    rows = await db.execute(
        select(
            Match.home_team_name,
            Match.league_id,
            Match.league_name,
            Match.home_team_logo,
        ).union(
            select(
                Match.away_team_name,
                Match.league_id,
                Match.league_name,
                Match.away_team_logo,
            )
        )
    )
    for name, league_id, league_name, logo in rows.all():
        if name and team_slug(name) == slug:
            return name, league_id, league_name, logo
    return None


async def _team_matches(db: AsyncSession, name: str) -> Dict[str, list]:
    """Jamoaning o'yinlari: tugaganlari yangisidan, bo'lajaklari yaqinidan."""
    tegishli = or_(Match.home_team_name == name, Match.away_team_name == name)

    recent = await db.execute(
        select(Match)
        .where(tegishli, Match.status == "FT")
        .order_by(Match.match_time.desc())
        .limit(RECENT_LIMIT)
    )
    upcoming = await db.execute(
        select(Match)
        .where(tegishli, Match.status.in_(("NS", "LIVE")))
        .order_by(Match.match_time.asc())
        .limit(UPCOMING_LIMIT)
    )
    return {
        "recent": list(recent.scalars().all()),
        "upcoming": list(upcoming.scalars().all()),
    }


async def _standing_row_for(
    db: AsyncSession, name: str, slug: str, league_id: Optional[int]
) -> Optional[dict]:
    """Turnir jadvalidagi qatori (bo'lsa).

    Jadvaldagi nom o'yinlardagi nomdan biroz farq qilishi mumkin, shuning
    uchun avval to'liq moslik, keyin slug bo'yicha moslik tekshiriladi.
    """
    from app.services.standings import get_standings

    tables = await get_standings(db, league_id=league_id)
    for table in tables:
        for row in table["table"]:
            if row["team"] == name:
                return row
        for row in table["table"]:
            if team_slug(row["team"]) == slug:
                return row
    return None

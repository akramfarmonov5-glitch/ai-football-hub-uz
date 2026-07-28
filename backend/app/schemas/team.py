from typing import List, Optional

from pydantic import BaseModel

from app.schemas.match import MatchResponse
from app.schemas.standings import TeamStanding


class TeamSummary(BaseModel):
    slug: str
    name: str
    badge: Optional[str] = None
    league_name: Optional[str] = None


class TeamDetail(TeamSummary):
    league_id: Optional[int] = None
    stadium: Optional[str] = None
    stadium_capacity: Optional[int] = None
    location: Optional[str] = None
    country: Optional[str] = None
    founded: Optional[int] = None
    website: Optional[str] = None
    # Tayyor tavsif: tarjima bo'lsa o'zbekcha, aks holda asl matn
    description: Optional[str] = None
    # Rost bo'lsa yuqoridagi matn AI tarjimasi
    description_translated: bool = False

    recent_matches: List[MatchResponse] = []
    upcoming_matches: List[MatchResponse] = []
    standing: Optional[TeamStanding] = None

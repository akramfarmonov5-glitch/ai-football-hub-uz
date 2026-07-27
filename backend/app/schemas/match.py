from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.clock import as_utc

class MatchBase(BaseModel):
    league_id: int
    league_name: str
    home_team_name: str
    away_team_name: str
    home_team_logo: Optional[str] = None
    away_team_logo: Optional[str] = None
    status: str
    score_home: int = 0
    score_away: int = 0
    match_time: datetime
    minute: Optional[int] = 0

    @field_validator("match_time")
    @classmethod
    def _mark_as_utc(cls, value: datetime) -> datetime:
        """Bazadagi naive vaqtga UTC belgisini qo'shadi.

        Busiz JSON'da `2026-07-05T01:29:37` chiqib, brauzer uni mahalliy vaqt
        deb o'qirdi va o'yin vaqti soatlarga siljirdi.
        """
        return as_utc(value)

class MatchCreate(MatchBase):
    pass

class MatchUpdate(BaseModel):
    status: Optional[str] = None
    score_home: Optional[int] = None
    score_away: Optional[int] = None
    minute: Optional[int] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    stats: Optional[Dict[str, Any]] = None
    ai_preview: Optional[str] = None
    ai_analysis: Optional[str] = None
    win_probability: Optional[Dict[str, Any]] = None

class MatchResponse(MatchBase):
    id: int
    lineups: Optional[Dict[str, Any]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    stats: Optional[Dict[str, Any]] = None
    ai_preview: Optional[str] = None
    ai_analysis: Optional[str] = None
    win_probability: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

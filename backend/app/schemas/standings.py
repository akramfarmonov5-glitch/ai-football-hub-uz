from typing import List, Literal, Optional

from pydantic import BaseModel


class TeamStanding(BaseModel):
    position: int
    team: str
    logo: Optional[str] = None
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    # Oxirgi 5 o'yin natijasi, eng yangisi oxirida: ["W", "D", "L", ...]
    form: List[Literal["W", "D", "L"]] = []


class LeagueStandings(BaseModel):
    league_id: int
    league_name: str
    table: List[TeamStanding]

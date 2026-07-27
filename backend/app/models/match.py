from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, index=True)
    league_name = Column(String, index=True)
    home_team_name = Column(String, index=True)
    away_team_name = Column(String, index=True)
    home_team_logo = Column(String, nullable=True)
    away_team_logo = Column(String, nullable=True)
    status = Column(String)  # 'NS' (Not Started), 'LIVE', 'FT' (Finished)
    score_home = Column(Integer, default=0)
    score_away = Column(Integer, default=0)
    match_time = Column(DateTime)
    minute = Column(Integer, nullable=True, default=0)
    
    # Complex fields
    lineups = Column(JSON, nullable=True)      # Lineups (players, formations)
    timeline = Column(JSON, nullable=True)     # list of events: goals, cards, subs
    stats = Column(JSON, nullable=True)        # possession, shots, xG
    ai_preview = Column(Text, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    win_probability = Column(JSON, nullable=True) # {home, draw, away}

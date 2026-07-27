from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Literal, Optional
from app.core.database import get_async_db
from app.core.security import verify_admin
from app.models.match import Match
from app.schemas.match import MatchResponse
from app.services.ai_engine import AIEngineService, get_ai_engine

router = APIRouter()

@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    db: AsyncSession = Depends(get_async_db),
    status: Optional[Literal["NS", "LIVE", "FT"]] = None,
    league_id: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """O'yinlar ro'yxati.

    Limit majburiy: busiz baza o'sgan sari javob ham cheksiz o'sib borardi.
    """
    query = select(Match)
    if status:
        query = query.where(Match.status == status)
    if league_id is not None:
        query = query.where(Match.league_id == league_id)

    query = query.order_by(Match.match_time.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/live", response_model=List[MatchResponse])
async def get_live_matches(
    db: AsyncSession = Depends(get_async_db),
    limit: int = Query(default=100, ge=1, le=200),
):
    result = await db.execute(
        select(Match)
        .where(Match.status == "LIVE")
        .order_by(Match.match_time.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, db: AsyncSession = Depends(get_async_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

# AI generatsiyasi pullik tashqi API'ga murojaat qiladi — himoyasiz qoldirilsa
# har qanday bot uni cheksiz chaqirib hisobni bo'shatishi mumkin.
@router.post("/{match_id}/preview", response_model=MatchResponse, dependencies=[Depends(verify_admin)])
async def generate_preview(match_id: int, db: AsyncSession = Depends(get_async_db), ai_service: AIEngineService = Depends(get_ai_engine)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.ai_preview = await ai_service.generate_match_preview(
        match.home_team_name, match.away_team_name, match.league_name
    )
    await db.commit()
    await db.refresh(match)
    return match

@router.post("/{match_id}/analysis", response_model=MatchResponse, dependencies=[Depends(verify_admin)])
async def generate_analysis(match_id: int, db: AsyncSession = Depends(get_async_db), ai_service: AIEngineService = Depends(get_ai_engine)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "FT":
        raise HTTPException(status_code=400, detail="Match must be finished to analyze")

    match.ai_analysis = await ai_service.generate_post_match_analysis(
        match.home_team_name,
        match.away_team_name,
        f"{match.score_home}-{match.score_away}",
        match.stats or {},
        match.timeline or []
    )
    await db.commit()
    await db.refresh(match)
    return match

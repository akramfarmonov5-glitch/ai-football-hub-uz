from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from app.core.database import get_async_db
from app.models.match import Match
from app.models.news import News
from app.schemas.match import MatchResponse
from app.services.football_api import FootballAPIService
from app.services.ai_engine import AIEngineService, get_ai_engine
from app.services.simulator import broadcast_updates

router = APIRouter()

class NewsGenerationRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)

class MatchOverrideRequest(BaseModel):
    score_home: int = Field(ge=0, le=99)
    score_away: int = Field(ge=0, le=99)
    status: Literal["NS", "LIVE", "FT"]
    minute: int = Field(ge=0, le=130)

@router.get("/verify")
async def verify_token():
    """Admin panel kiritilgan tokenni tekshirish uchun chaqiradi.

    Router darajasidagi `verify_admin` dependency ishlaydi: token noto'g'ri
    bo'lsa bu yergacha yetib kelinmaydi (401 qaytadi).
    """
    return {"ok": True}

@router.post("/seed")
async def seed_data(db: AsyncSession = Depends(get_async_db)):
    await FootballAPIService(db).seed_mock_matches_if_empty()
    return {"message": "Mock data seeded (if database was empty)."}

@router.post("/simulate")
async def trigger_simulation(db: AsyncSession = Depends(get_async_db)):
    updated_matches = await FootballAPIService(db).simulate_live_updates()
    await broadcast_updates(db, updated_matches)
    return {"message": f"Simulated {len(updated_matches)} live matches."}

@router.post("/generate-news")
async def generate_ai_news(req: NewsGenerationRequest, db: AsyncSession = Depends(get_async_db), ai_service: AIEngineService = Depends(get_ai_engine)):
    article_data = await ai_service.generate_news_article(req.topic)

    # Import slugify locally to reuse logic
    from app.api.endpoints.news import slugify
    base_slug = slugify(article_data["title"])
    slug = base_slug
    counter = 1
    while await db.scalar(select(News).where(News.slug == slug)):
        slug = f"{base_slug}-{counter}"
        counter += 1

    news_item = News(
        title=article_data["title"],
        slug=slug,
        summary=article_data["summary"],
        content=article_data["content"],
        tags=article_data["tags"],
        is_published=True
    )
    db.add(news_item)
    await db.commit()
    await db.refresh(news_item)
    return news_item

@router.put("/matches/{match_id}", response_model=MatchResponse)
async def manual_match_override(match_id: int, override: MatchOverrideRequest, db: AsyncSession = Depends(get_async_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.score_home = override.score_home
    match.score_away = override.score_away
    match.status = override.status
    match.minute = override.minute

    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match

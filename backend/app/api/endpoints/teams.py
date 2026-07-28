from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.team import TeamDetail, TeamSummary
from app.services.teams import get_team_page, list_teams

router = APIRouter()


@router.get("/", response_model=List[TeamSummary])
async def read_teams(db: AsyncSession = Depends(get_async_db)):
    """Profili mavjud jamoalar ro'yxati."""
    return await list_teams(db)


@router.get("/{slug}", response_model=TeamDetail)
async def read_team(slug: str, db: AsyncSession = Depends(get_async_db)):
    """Jamoa sahifasi: profil, o'yinlar va turnir jadvalidagi o'rni."""
    team = await get_team_page(db, slug)
    if team is None:
        raise HTTPException(status_code=404, detail="Jamoa topilmadi")
    return team

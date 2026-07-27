from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.standings import LeagueStandings
from app.services.standings import get_standings

router = APIRouter()


@router.get("/", response_model=List[LeagueStandings])
async def read_standings(
    db: AsyncSession = Depends(get_async_db),
    league_id: Optional[int] = None,
):
    """Turnir jadvallari — tugagan o'yinlardan hisoblanadi.

    `league_id` berilsa faqat o'sha liga qaytariladi.
    """
    return await get_standings(db, league_id)

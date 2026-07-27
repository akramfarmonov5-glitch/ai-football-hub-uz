from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/")
async def read_meta():
    """Ma'lumot manbai haqida.

    Frontend shu javobga qarab foydalanuvchini ogohlantiradi: simulyatsiya
    rejimida o'yinlar va natijalar to'qib chiqariladi, ularni haqiqiy deb
    ko'rsatish mumkin emas.
    """
    if settings.API_FOOTBALL_KEY:
        source = "api-football"
    elif settings.SPORTSDB_ENABLED and settings.sportsdb_league_ids:
        source = "thesportsdb"
    else:
        source = "simulation"

    return {
        "data_source": source,
        "is_simulated": not settings.uses_real_data,
        "ai_enabled": bool(settings.GEMINI_API_KEY or settings.vertex_project),
        # Bepul TheSportsDB tarifida jonli daqiqama-daqiqa hisob yo'q
        "has_live_scores": source == "api-football",
    }

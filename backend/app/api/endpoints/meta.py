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
    live = bool(settings.API_FOOTBALL_KEY)
    return {
        "data_source": "api-football" if live else "simulation",
        "is_simulated": not live,
        "ai_enabled": bool(settings.GEMINI_API_KEY or settings.vertex_project),
    }

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.ai_engine import get_ai_engine
from app.services.football_api import FootballAPIService
from app.services.websocket import manager

logger = logging.getLogger(__name__)


def _match_update_payload(match) -> dict:
    """Shape a Match ORM object into the WebSocket 'match_update' event."""
    return {
        "event": "match_update",
        "match": {
            "id": match.id,
            "score_home": match.score_home,
            "score_away": match.score_away,
            "status": match.status,
            "minute": match.minute,
            "timeline": match.timeline,
            "stats": match.stats,
            "win_probability": match.win_probability,
        },
    }


async def broadcast_updates(db: AsyncSession, updated_matches: list) -> None:
    """Broadcast each updated match over WebSocket and generate post-match
    AI analysis for freshly finished games. Shared by the background loop
    and the manual /admin/simulate endpoint (single source of truth)."""
    ai_service = get_ai_engine()
    for match in updated_matches:
        await manager.broadcast(_match_update_payload(match))

        if match.status == "FT" and not match.ai_analysis:
            match.ai_analysis = await ai_service.generate_post_match_analysis(
                match.home_team_name,
                match.away_team_name,
                f"{match.score_home}-{match.score_away}",
                match.stats or {},
                match.timeline or [],
            )
            db.add(match)
            await db.commit()


async def run_simulation_loop(interval_seconds: int = 10) -> None:
    """Fon vazifasi: har N soniyada o'yinlarni oldinga suradi va tarqatadi."""
    logger.info("Simulyator ishga tushdi (interval: %ds)", interval_seconds)
    while True:
        await asyncio.sleep(interval_seconds)
        async with AsyncSessionLocal() as db:
            try:
                updated_matches = await FootballAPIService(db).simulate_live_updates()
                if updated_matches:
                    await broadcast_updates(db, updated_matches)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Simulyatsiya siklida xato")

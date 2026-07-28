from fastapi import APIRouter, Depends
from app.api.endpoints import matches, news, admin, meta, standings, teams
from app.core.security import verify_admin

api_router = APIRouter()

api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(standings.router, prefix="/standings", tags=["standings"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_admin)],
)

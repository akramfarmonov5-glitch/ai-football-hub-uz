import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.migrations import run_migrations
from app.services.football_api import FootballAPIService
from app.services.simulator import run_simulation_loop
from app.services.websocket import manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def start_telegram_bot():
    """TELEGRAM_BOT_TOKEN sozlangan bo'lsa aiogram botini fonda ishga tushiradi."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    try:
        from aiogram import Bot, Dispatcher
        from bot.handlers import commands, matches, settings as settings_handler

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(commands.router)
        dp.include_router(matches.router)
        dp.include_router(settings_handler.router)

        logger.info("Telegram Bot polling ishga tushirildi...")
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.error("Telegram bot polling xatosi: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Sxemani Alembic boshqaradi. `to_thread` — migratsiyalar sinxron
    # drayverda ishlaydi va event loop'ni bloklamasligi kerak.
    await asyncio.to_thread(run_migrations)

    async with AsyncSessionLocal() as db:
        await FootballAPIService(db).seed_mock_matches_if_empty()

    if not settings.ADMIN_TOKEN:
        logger.warning(
            "ADMIN_TOKEN sozlanmagan — admin va yozish endpointlari ishlamaydi. "
            "backend/.env faylida uni belgilang."
        )

    simulator_task = asyncio.create_task(run_simulation_loop())
    bot_task = asyncio.create_task(start_telegram_bot())

    yield

    # --- Shutdown ---
    simulator_task.cancel()
    bot_task.cancel()
    try:
        await asyncio.gather(simulator_task, bot_task, return_exceptions=True)
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Football Hub Uzbekistan API with simulated real-time updates and AI commentary.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS — explicit front-end origins only (never "*" with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["service"])
async def root():
    """Xizmat ishlayotganini bildiruvchi oddiy javob."""
    return {
        "service": settings.PROJECT_NAME,
        "version": app.version,
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health", tags=["service"])
async def health():
    """Monitoring va deploy healthcheck uchun — bazaga ham murojaat qiladi."""
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        database_ok = True
    except Exception as exc:  # pragma: no cover - faqat nosozlik holatida
        logger.error("Healthcheck: bazaga ulanib bo'lmadi: %s", exc)
        database_ok = False

    return {
        "status": "ok" if database_ok else "degraded",
        "database": "ok" if database_ok else "error",
        "websocket_clients": len(manager.active_connections),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Ulanishni ochiq tutamiz va mijoz heartbeat'iga javob beramiz
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        logger.exception("WebSocket xatosi")
        await manager.disconnect(websocket)

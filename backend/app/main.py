import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, async_engine, AsyncSessionLocal
from app.api.router import api_router
from app.services.football_api import FootballAPIService
from app.services.websocket import manager
from app.services.simulator import run_simulation_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        await FootballAPIService(db).seed_mock_matches_if_empty()

    simulator_task = asyncio.create_task(run_simulation_loop())

    yield

    # --- Shutdown ---
    simulator_task.cancel()
    try:
        await simulator_task
    except asyncio.CancelledError:
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open and listen for client heartbeats/messages
            data = await websocket.receive_text()
            # Respond to ping/heartbeat if necessary
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

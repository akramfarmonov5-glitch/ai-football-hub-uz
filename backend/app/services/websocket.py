import asyncio
import json
import logging
from typing import Any, Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Jonli yangilanishlarni barcha ulangan mijozlarga tarqatadi."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        # Bir vaqtda bir nechta tarqatish ketayotganda ro'yxatni himoyalash
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info("WebSocket ulandi (jami: %d)", len(self.active_connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info("WebSocket uzildi (jami: %d)", len(self.active_connections))

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Xabarni hammaga yuboradi, javob bermagan ulanishlarni tozalaydi.

        Muhim: ilgari ro'yxat aynan sikl ichida o'zgartirilardi — natijada
        keyingi elementlar tashlab ketilardi va o'lik ulanishlar yig'ilib
        qolardi. Endi avval nusxa bo'yicha yuriladi, tozalash keyin.
        """
        if not self.active_connections:
            return

        payload = json.dumps(message)
        stale: List[WebSocket] = []

        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception:
                stale.append(connection)

        for connection in stale:
            await self.disconnect(connection)

        if stale:
            logger.info("%d ta ishlamayotgan WebSocket tozalandi", len(stale))


manager = ConnectionManager()

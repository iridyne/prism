from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ProgressHub:
    """Broadcasts task progress events to websocket subscribers."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, task_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[task_id].add(websocket)

    async def disconnect(self, task_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._connections.get(task_id)
            if not sockets:
                return
            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(task_id, None)

    async def publish(self, task_id: str, payload: dict) -> None:
        async with self._lock:
            sockets = list(self._connections.get(task_id, set()))

        disconnected: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                disconnected.append(ws)

        if not disconnected:
            return

        async with self._lock:
            live = self._connections.get(task_id)
            if not live:
                return
            for ws in disconnected:
                live.discard(ws)
            if not live:
                self._connections.pop(task_id, None)

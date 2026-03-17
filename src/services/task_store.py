from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskState:
    task_id: str
    portfolio_id: str
    status: str
    progress: int
    message: str
    timestamp: datetime
    error: str | None = None


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskState] = {}
        self._lock = asyncio.Lock()

    async def put(self, state: TaskState) -> None:
        async with self._lock:
            self._tasks[state.task_id] = state

    async def get(self, task_id: str) -> TaskState | None:
        async with self._lock:
            return self._tasks.get(task_id)

    async def update(
        self,
        task_id: str,
        *,
        status: str | None = None,
        progress: int | None = None,
        message: str | None = None,
        error: str | None = None,
    ) -> TaskState | None:
        async with self._lock:
            state = self._tasks.get(task_id)
            if state is None:
                return None
            if status is not None:
                state.status = status
            if progress is not None:
                state.progress = progress
            if message is not None:
                state.message = message
            if error is not None:
                state.error = error
            state.timestamp = datetime.utcnow()
            return state

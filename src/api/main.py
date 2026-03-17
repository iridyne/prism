from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.dependencies import get_progress_hub
from src.api.routes import analysis, data, portfolios, tasks
from src.config import settings
from src.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Prism API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolios.router)
app.include_router(analysis.router)
app.include_router(tasks.router)
app.include_router(data.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Prism AI Portfolio Analysis API"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.websocket("/ws/tasks/{task_id}")
async def task_progress_socket(websocket: WebSocket, task_id: str) -> None:
    hub = get_progress_hub()
    await hub.connect(task_id, websocket)
    try:
        while True:
            # Keep connection alive; server pushes progress via hub.publish.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await hub.disconnect(task_id, websocket)
    except Exception:
        await hub.disconnect(task_id, websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_analysis_service
from src.api.schemas import TaskStatusResponse
from src.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    task = await analysis_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(
        task_id=task.task_id,
        portfolio_id=task.portfolio_id,
        status=task.status,
        progress=task.progress,
        message=task.message,
        timestamp=task.timestamp,
        error=task.error,
    )

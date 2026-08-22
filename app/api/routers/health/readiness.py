"""Runtime readiness endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.schemas.responses import ApplicationResponse, ReadinessResult

from .dependencies import ensure_postgresql_ready

router = APIRouter()


@router.get(
    path="/health.checkReadiness",
    response_model=ApplicationResponse[ReadinessResult],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Check runtime readiness",
    description="Report readiness after a lightweight probe of required PostgreSQL connectivity.",
    operation_id="authService.health.checkReadiness",
    openapi_extra={
        "x-pokerlost-authz": {
            "public": True,
        },
    },
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[None],
            "description": "A required runtime dependency is unavailable.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
            "description": "Sanitized internal failure.",
        },
    },
    tags=["health"],
)
async def check_readiness(
    _: Annotated[None, Depends(ensure_postgresql_ready)],
) -> dict[str, object]:
    """Return ready after all required dependency probes succeed."""
    return {
        "ok": True,
        "result": {
            "status": "ready",
            "dependencies": {
                "postgresql": "ready",
            },
        },
    }

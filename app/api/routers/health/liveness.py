"""Process liveness endpoint."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.responses import ApplicationResponse, LivenessResult

router = APIRouter()


@router.get(
    path="/health.checkLiveness",
    response_model=ApplicationResponse[LivenessResult],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Check process liveness",
    description="Report whether this application process can handle HTTP requests.",
    operation_id="health.checkLiveness",
    openapi_extra={
        "x-pokerlost-authz": {
            "public": True,
        },
    },
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
            "description": "Sanitized internal failure.",
        },
    },
    tags=["health"],
)
async def check_liveness() -> dict[str, object]:
    """Return healthy without consulting external dependencies."""
    return {
        "ok": True,
        "result": {
            "status": "healthy",
        },
    }

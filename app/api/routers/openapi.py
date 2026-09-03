"""Public OpenAPI JSON publication router."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request, status

router = APIRouter(tags=["openapi"])


@router.get(
    path="/getOpenApi",
    operation_id="getOpenApi",
    status_code=status.HTTP_200_OK,
    summary="Get the OpenAPI JSON document",
    description="Return the generated service contract.",
)
async def get_open_api(request: Request) -> dict[str, object]:
    """Return the unmodified FastAPI OpenAPI document."""
    return cast(dict[str, object], request.app.openapi())

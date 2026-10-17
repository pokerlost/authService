"""Liveness and enabled-dependency readiness routes."""

from __future__ import annotations

import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from authservice.resources import ApplicationResources, get_resources

router = APIRouter(include_in_schema=False)


@router.get("/health/live")
async def live() -> dict[str, str]:
    """Confirm the process can answer HTTP without querying dependencies."""
    return {"status": "alive"}


@router.get("/health/ready")
async def ready(
    resources: Annotated[ApplicationResources, Depends(get_resources)],
) -> dict[str, str]:
    """Check only resources enabled for this application."""
    try:
        async with asyncio.timeout(2.0):
            async with resources.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
    except (OSError, TimeoutError, SQLAlchemyError) as exc:
        logging.getLogger("authService").warning("Required database unavailable")
        raise HTTPException(
            status_code=503, detail="Required dependency unavailable"
        ) from exc
    return {"status": "ready"}

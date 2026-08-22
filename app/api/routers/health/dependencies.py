"""Health-specific dependency checks."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.dependencies import get_application_resources
from api.errors.database import DatabaseUnavailableError
from api.resources import ApplicationResources


async def ensure_postgresql_ready(
    resources: Annotated[ApplicationResources, Depends(get_application_resources)],
) -> None:
    """Execute one lightweight probe against the required PostgreSQL database."""
    try:
        async with resources.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except (OSError, SQLAlchemyError) as exception:
        raise DatabaseUnavailableError from exception

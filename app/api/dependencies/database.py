"""Transactional database session dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors.database import DatabaseUnavailableError
from api.resources import ApplicationResources

from .resources import get_application_resources


async def get_database_session(
    resources: Annotated[ApplicationResources, Depends(get_application_resources)],
) -> AsyncIterator[AsyncSession]:
    """Yield one request-owned transaction and normalize connectivity failures."""
    try:
        async with resources.session_factory.begin() as session:
            yield session
    except (OSError, OperationalError) as exception:
        raise DatabaseUnavailableError from exception

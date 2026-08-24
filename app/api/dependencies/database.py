"""Request-scoped transactional SQLAlchemy session dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors.database import DatabaseUnavailableError

from .resources import ApplicationResourcesDep


async def get_database_session(
    resources: ApplicationResourcesDep,
) -> AsyncIterator[AsyncSession]:
    """Yield one transaction that commits before the response is sent."""
    try:
        async with resources.session_factory.begin() as session:
            yield session
    except (OSError, OperationalError) as exception:
        raise DatabaseUnavailableError from exception


type DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session, scope="function"),
]

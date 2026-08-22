"""Concrete runtime resources owned by the API composition root."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from configuration import Settings
from persistence.database import create_session_factory


@dataclass(frozen=True, slots=True)
class ApplicationResources:
    """Process-level resources shared by request dependencies."""

    settings: Settings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]


def create_application_resources(settings: Settings) -> ApplicationResources:
    """Create the engine and session factory without opening a connection."""
    database = settings.database
    engine = create_async_engine(
        database.url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=database.pool_size,
        max_overflow=database.max_overflow,
        pool_timeout=database.pool_timeout_seconds,
        connect_args={
            "command_timeout": database.command_timeout_seconds,
            "server_settings": {
                "application_name": settings.application.service_name,
            },
        },
        hide_parameters=True,
    )
    return ApplicationResources(
        settings=settings,
        engine=engine,
        session_factory=create_session_factory(engine),
    )

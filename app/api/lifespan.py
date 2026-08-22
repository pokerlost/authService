"""Application runtime resource lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from application.security import SigningKeyProvider
from configuration import Settings
from observability import instrument_database
from persistence.database import create_database_engine, create_session_factory

from .resources import ApplicationResources


def create_lifespan(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None, bool | None]]:
    """Create runtime database and signing resources during application startup."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine = create_database_engine(
            settings.database,
            application_name=settings.application.service_name,
        )
        signing_key_provider = SigningKeyProvider(settings.jwt)
        try:
            instrument_database(engine)
            resources = ApplicationResources(
                engine=engine,
                session_factory=create_session_factory(engine),
                signing_key_provider=signing_key_provider,
            )
            application.state.resources = resources
            application.state.settings = settings
            yield
        finally:
            application.state.resources = None
            application.state.settings = None
            await engine.dispose()

    return lifespan

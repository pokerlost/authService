"""Application resource lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from .resources import ApplicationResources


def create_lifespan(
    resources: ApplicationResources,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None, bool | None]]:
    """Create a lifespan that deterministically releases runtime resources."""

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await resources.engine.dispose()

    return lifespan

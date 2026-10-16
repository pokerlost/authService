"""Typed, lifespan-owned process resources and narrow request access."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


@dataclass(frozen=True, slots=True)
class ApplicationResources:
    """Resources owned by exactly one ASGI lifespan and worker."""

    engine: AsyncEngine
    sessionFactory: async_sessionmaker[AsyncSession]


def getResources(request: Request) -> ApplicationResources:
    """Expose initialized resources through one narrow dependency."""
    resources = getattr(request.app.state, "resources", None)
    if not isinstance(resources, ApplicationResources):
        raise RuntimeError("Application resources are not initialized")
    return resources

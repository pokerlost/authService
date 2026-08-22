"""Runtime resources owned by the application lifespan."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.security import SigningKeyProvider


class ApplicationResources:
    """Application runtime objects shared by request dependencies."""

    __slots__ = ("engine", "session_factory", "signing_key_provider")

    def __init__(
        self,
        *,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        signing_key_provider: SigningKeyProvider,
    ) -> None:
        self.engine = engine
        self.session_factory = session_factory
        self.signing_key_provider = signing_key_provider

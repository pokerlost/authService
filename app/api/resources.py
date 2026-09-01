"""Runtime resources owned by the application lifespan."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.idempotency import BusinessOperationFingerprinter
from application.ports import ServiceAccessTokenSigner


@dataclass(frozen=True, slots=True)
class ApplicationResources:
    """Reusable process resources shared by request dependencies."""

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    business_operation_fingerprinter: BusinessOperationFingerprinter
    service_access_token_signer: ServiceAccessTokenSigner

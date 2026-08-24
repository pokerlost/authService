"""SQLAlchemy AUTO service credential repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert

from domain.enums import ServiceCredentialStatus
from persistence.database.models import ServiceCredentialModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyServiceCredentialRepository(SQLAlchemyEntityRepository[ServiceCredentialModel]):
    """Persist finite digest-only service credentials and revocation state."""

    model = ServiceCredentialModel

    async def create(
        self,
        *,
        service_principal_id: UUID,
        client_id: str,
        secret_digest: bytes,
        expires_at: datetime,
    ) -> ServiceCredentialModel | None:
        """Insert a credential or return no row on an improbable client-ID collision."""
        result = await self._read_scalar(
            insert(ServiceCredentialModel)
            .values(
                service_principal_id=service_principal_id,
                client_id=client_id,
                secret_digest=secret_digest,
                status=ServiceCredentialStatus.ACTIVE,
                expires_at=expires_at,
            )
            .on_conflict_do_nothing(index_elements=[ServiceCredentialModel.client_id])
            .returning(ServiceCredentialModel),
        )
        return result.one_or_none()

    async def get_by_client_id(self, client_id: str) -> ServiceCredentialModel | None:
        """Return one service credential by its public random identifier."""
        result = await self._read_scalar(
            select(ServiceCredentialModel).where(ServiceCredentialModel.client_id == client_id),
        )
        return result.one_or_none()

    async def revoke(
        self,
        *,
        client_id: str,
        revoked_at: datetime,
    ) -> ServiceCredentialModel | None:
        """Idempotently revoke one known credential while preserving its first timestamp."""
        result = await self._read_scalar(
            update(ServiceCredentialModel)
            .where(ServiceCredentialModel.client_id == client_id)
            .values(
                status=ServiceCredentialStatus.REVOKED,
                revoked_at=func.coalesce(ServiceCredentialModel.revoked_at, revoked_at),
            )
            .returning(ServiceCredentialModel),
        )
        return result.one_or_none()

"""SQLAlchemy registered-service repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from domain.types import ServiceId
from persistence.database.models import RegisteredServiceModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyRegisteredServiceRepository(SQLAlchemyEntityRepository[RegisteredServiceModel]):
    """Persist and lock platform service identities derived from contracts."""

    model = RegisteredServiceModel

    async def create(self, service_id: ServiceId) -> RegisteredServiceModel | None:
        """Insert one service or return no row on a concurrent identity conflict."""
        result = await self._read_scalar(
            insert(RegisteredServiceModel)
            .values(service_id=service_id)
            .on_conflict_do_nothing(index_elements=[RegisteredServiceModel.service_id])
            .returning(RegisteredServiceModel),
        )
        return result.one_or_none()

    async def get_by_service_id(self, service_id: ServiceId) -> RegisteredServiceModel | None:
        """Return one exact case-sensitive platform service identity."""
        result = await self._read_scalar(
            select(RegisteredServiceModel).where(RegisteredServiceModel.service_id == service_id),
        )
        return result.one_or_none()

    async def get_by_id_for_update(
        self,
        registered_service_id: UUID,
    ) -> RegisteredServiceModel | None:
        """Lock one service row to serialize its activation lifecycle."""
        result = await self._read_scalar(
            select(RegisteredServiceModel)
            .where(RegisteredServiceModel.id == registered_service_id)
            .with_for_update(),
        )
        return result.one_or_none()

"""SQLAlchemy AUTO audience grant repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from domain.types import ServiceSlug
from persistence.database.models import ServiceAudienceGrantModel

from .base import SQLAlchemyRepository


class SQLAlchemyServiceAudienceGrantRepository(SQLAlchemyRepository):
    """Persist explicit source-principal to target-audience grants."""

    async def grant(self, *, service_principal_id: UUID, audience: ServiceSlug) -> bool:
        """Idempotently create one audience grant."""
        result = await self._read_scalar(
            insert(ServiceAudienceGrantModel)
            .values(
                service_principal_id=service_principal_id,
                audience=audience,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    ServiceAudienceGrantModel.service_principal_id,
                    ServiceAudienceGrantModel.audience,
                ],
            )
            .returning(ServiceAudienceGrantModel.service_principal_id),
        )
        return result.one_or_none() is not None

    async def revoke(self, *, service_principal_id: UUID, audience: ServiceSlug) -> bool:
        """Idempotently remove one audience grant."""
        result = await self._read_scalar(
            delete(ServiceAudienceGrantModel)
            .where(
                ServiceAudienceGrantModel.service_principal_id == service_principal_id,
                ServiceAudienceGrantModel.audience == audience,
            )
            .returning(ServiceAudienceGrantModel.service_principal_id),
        )
        return result.one_or_none() is not None

    async def has_grant(self, *, service_principal_id: UUID, audience: ServiceSlug) -> bool:
        """Report whether one exact source-to-target grant exists."""
        result = await self._read_scalar(
            select(ServiceAudienceGrantModel.service_principal_id).where(
                ServiceAudienceGrantModel.service_principal_id == service_principal_id,
                ServiceAudienceGrantModel.audience == audience,
            ),
        )
        return result.one_or_none() is not None

"""SQLAlchemy AUTO service principal repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from domain.types import ServiceSlug
from persistence.database.models import ServicePrincipalModel

from .base import SQLAlchemyRepository


class SQLAlchemyServicePrincipalRepository(SQLAlchemyRepository):
    """Persist and locate canonical machine service identities."""

    async def create(
        self,
        *,
        principal_id: UUID,
        service_slug: ServiceSlug,
    ) -> ServicePrincipalModel | None:
        """Insert a service identity or return no row on a slug conflict."""
        result = await self._read_scalar(
            insert(ServicePrincipalModel)
            .values(
                principal_id=principal_id,
                service_slug=service_slug,
            )
            .on_conflict_do_nothing(index_elements=[ServicePrincipalModel.service_slug])
            .returning(ServicePrincipalModel),
        )
        return result.one_or_none()

    async def get_by_principal_id(self, principal_id: UUID) -> ServicePrincipalModel | None:
        """Return the service identity attached to one principal."""
        result = await self._read_scalar(
            select(ServicePrincipalModel).where(
                ServicePrincipalModel.principal_id == principal_id
            ),
        )
        return result.one_or_none()

    async def get_by_service_slug(self, service_slug: ServiceSlug) -> ServicePrincipalModel | None:
        """Return the service identity with one canonical slug."""
        result = await self._read_scalar(
            select(ServicePrincipalModel).where(
                ServicePrincipalModel.service_slug == service_slug
            ),
        )
        return result.one_or_none()

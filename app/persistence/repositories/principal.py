"""SQLAlchemy principal repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert, select, update

from domain.enums import PrincipalStatus, Role
from persistence.database.models import PrincipalModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyPrincipalRepository(SQLAlchemyEntityRepository[PrincipalModel]):
    """Persist and load authentication principals."""

    model = PrincipalModel

    async def create(
        self,
        *,
        role: Role,
        status: PrincipalStatus,
    ) -> PrincipalModel:
        """Insert and return one principal."""
        result = await self._read_scalar(
            insert(PrincipalModel)
            .values(
                role=role,
                status=status,
            )
            .returning(PrincipalModel),
        )
        return result.one()

    async def get_by_id_for_update(self, principal_id: UUID) -> PrincipalModel | None:
        """Lock and return one principal for a serialized status transition."""
        result = await self._read_scalar(
            select(PrincipalModel).where(PrincipalModel.id == principal_id).with_for_update(),
        )
        return result.one_or_none()

    async def set_status(
        self,
        *,
        principal_id: UUID,
        status: PrincipalStatus,
    ) -> PrincipalModel | None:
        """Set and return one principal's authentication status."""
        result = await self._read_scalar(
            update(PrincipalModel)
            .where(PrincipalModel.id == principal_id)
            .values(status=status)
            .returning(PrincipalModel),
        )
        return result.one_or_none()

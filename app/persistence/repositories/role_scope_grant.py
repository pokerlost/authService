"""SQLAlchemy explicit human role scope grant repository."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from domain.enums import Role
from persistence.database.models import RoleScopeGrantModel

from .base import SQLAlchemyRepository


class SQLAlchemyRoleScopeGrantRepository(SQLAlchemyRepository):
    """Persist exact direct human role-to-operation scope grants."""

    async def grant(self, *, role: Role, api_operation_id: str) -> bool:
        """Idempotently grant one scope and report whether a row was created."""
        result = await self._read_scalar(
            insert(RoleScopeGrantModel)
            .values(role=role, api_operation_id=api_operation_id)
            .on_conflict_do_nothing(
                index_elements=[
                    RoleScopeGrantModel.role,
                    RoleScopeGrantModel.api_operation_id,
                ]
            )
            .returning(RoleScopeGrantModel.api_operation_id),
        )
        return result.one_or_none() is not None

    async def revoke(self, *, role: Role, api_operation_id: str) -> bool:
        """Idempotently revoke one scope and report whether a row was removed."""
        result = await self._read_scalar(
            delete(RoleScopeGrantModel)
            .where(
                RoleScopeGrantModel.role == role,
                RoleScopeGrantModel.api_operation_id == api_operation_id,
            )
            .returning(RoleScopeGrantModel.api_operation_id),
        )
        return result.one_or_none() is not None

    async def list_all(self, *, limit: int) -> list[RoleScopeGrantModel]:
        """Return a bounded deterministic role grant list."""
        result = await self._read_scalar(
            select(RoleScopeGrantModel)
            .order_by(RoleScopeGrantModel.role, RoleScopeGrantModel.api_operation_id)
            .limit(limit),
        )
        return result.all()

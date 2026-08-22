"""SQLAlchemy principal repository."""

from __future__ import annotations

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.enums import PrincipalStatus, Role
from persistence.database.models import Principal

from .base import SQLAlchemyEntityRepository


class SQLAlchemyPrincipalRepository(SQLAlchemyEntityRepository[Principal]):
    """Persist and load authentication principals."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Principal)

    async def create(self, *, role: Role, status: PrincipalStatus) -> Principal:
        """Insert and return one principal."""
        statement = insert(Principal).values(role=role, status=status).returning(Principal)
        result = await self._execute_scalars(statement)
        return result.one()

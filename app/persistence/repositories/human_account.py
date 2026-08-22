"""SQLAlchemy human account repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from persistence.database.models import HumanAccount

from .base import SQLAlchemyRepository


class SQLAlchemyHumanAccountRepository(SQLAlchemyRepository):
    """Persist normalized human authentication identities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        *,
        principal_id: UUID,
        email: str,
        normalized_email: str,
    ) -> HumanAccount | None:
        """Insert an account or return no row on normalized email conflict."""
        statement = (
            insert(HumanAccount)
            .values(
                principal_id=principal_id,
                email=email,
                normalized_email=normalized_email,
            )
            .on_conflict_do_nothing(index_elements=[HumanAccount.normalized_email])
            .returning(HumanAccount)
        )
        result = await self._execute_scalars(statement)
        return result.one_or_none()

"""SQLAlchemy password credential repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from persistence.database.models import PasswordCredential

from .base import SQLAlchemyRepository


class SQLAlchemyPasswordCredentialRepository(SQLAlchemyRepository):
    """Persist Argon2id credentials separately from human identity metadata."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(
        self,
        *,
        principal_id: UUID,
        password_hash: str,
    ) -> PasswordCredential:
        """Insert and return one password credential."""
        statement = (
            insert(PasswordCredential)
            .values(principal_id=principal_id, password_hash=password_hash)
            .returning(PasswordCredential)
        )
        result = await self._execute_scalars(statement)
        return result.one()

"""SQLAlchemy password credential repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import insert, select, update

from persistence.database.models import PasswordCredentialModel

from .base import SQLAlchemyRepository


class SQLAlchemyPasswordCredentialRepository(SQLAlchemyRepository):
    """Persist Argon2id credentials separately from principal state."""

    async def create(
        self,
        *,
        principal_id: UUID,
        password_hash: str,
    ) -> PasswordCredentialModel:
        """Insert and return one password credential."""
        result = await self._read_scalar(
            insert(PasswordCredentialModel)
            .values(
                principal_id=principal_id,
                password_hash=password_hash,
            )
            .returning(PasswordCredentialModel),
        )
        return result.one()

    async def get_by_principal_id(self, principal_id: UUID) -> PasswordCredentialModel | None:
        """Return the password credential owned by one principal."""
        result = await self._read_scalar(
            select(PasswordCredentialModel).where(
                PasswordCredentialModel.principal_id == principal_id,
            ),
        )
        return result.one_or_none()

    async def get_by_principal_id_for_update(
        self,
        principal_id: UUID,
    ) -> PasswordCredentialModel | None:
        """Lock and return one password credential for a serialized lifecycle change."""
        result = await self._read_scalar(
            select(PasswordCredentialModel)
            .where(PasswordCredentialModel.principal_id == principal_id)
            .with_for_update(),
        )
        return result.one_or_none()

    async def replace_password(
        self,
        *,
        principal_id: UUID,
        password_hash: str,
        password_changed_at: datetime,
    ) -> PasswordCredentialModel | None:
        """Replace a verified human password and advance its security timestamp."""
        result = await self._read_scalar(
            update(PasswordCredentialModel)
            .where(PasswordCredentialModel.principal_id == principal_id)
            .values(
                password_hash=password_hash,
                password_changed_at=password_changed_at,
            )
            .returning(PasswordCredentialModel),
        )
        return result.one_or_none()

    async def replace_hash_for_rehash(
        self,
        *,
        principal_id: UUID,
        password_hash: str,
    ) -> PasswordCredentialModel | None:
        """Replace only the encoded hash after a successful policy rehash."""
        result = await self._read_scalar(
            update(PasswordCredentialModel)
            .where(PasswordCredentialModel.principal_id == principal_id)
            .values(password_hash=password_hash)
            .returning(PasswordCredentialModel),
        )
        return result.one_or_none()

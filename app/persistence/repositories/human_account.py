"""SQLAlchemy human account repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import contains_eager

from domain.enums import Role
from persistence.database.models import HumanAccountModel, PrincipalModel

from .base import SQLAlchemyRepository


class SQLAlchemyHumanAccountRepository(SQLAlchemyRepository):
    """Persist and locate canonical human login identities."""

    async def create(
        self,
        *,
        principal_id: UUID,
        username: str,
        nickname: str,
    ) -> HumanAccountModel | None:
        """Insert an account or return no row on a concurrent username conflict."""
        result = await self._read_scalar(
            insert(HumanAccountModel)
            .values(
                principal_id=principal_id,
                username=username,
                nickname=nickname,
            )
            .on_conflict_do_nothing(index_elements=[HumanAccountModel.username])
            .returning(HumanAccountModel),
        )
        return result.one_or_none()

    async def get_by_username(self, username: str) -> HumanAccountModel | None:
        """Return the human account with one canonical username."""
        result = await self._read_scalar(
            select(HumanAccountModel).where(HumanAccountModel.username == username),
        )
        return result.one_or_none()

    async def get_user_by_username(self, username: str) -> HumanAccountModel | None:
        """Return one ordinary-user account with its principal loaded explicitly."""
        result = await self._read_scalar(
            select(HumanAccountModel)
            .join(PrincipalModel, PrincipalModel.id == HumanAccountModel.principal_id)
            .options(contains_eager(HumanAccountModel.principal))
            .where(
                HumanAccountModel.username == username,
                PrincipalModel.role == Role.USER,
            ),
        )
        return result.one_or_none()

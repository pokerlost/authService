"""Role scope list query handler."""

from __future__ import annotations

from persistence.database.models import RoleScopeGrantModel
from persistence.repositories import SQLAlchemyRoleScopeGrantRepository

from .query import ListRoleScopesQuery


class ListRoleScopesHandler:
    """Return a deterministic bounded view of explicit direct role grants."""

    __slots__ = ("_repository",)

    def __init__(self, repository: SQLAlchemyRoleScopeGrantRepository) -> None:
        self._repository = repository

    async def execute(self, query: ListRoleScopesQuery) -> list[RoleScopeGrantModel]:
        """List persisted grants without applying inheritance."""
        return await self._repository.list_all(limit=query.limit)

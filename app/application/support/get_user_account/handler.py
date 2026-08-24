"""Support-safe ordinary-user account lookup."""

from __future__ import annotations

from application.errors.support import UserAccountNotFound
from domain.types import canonicalize_username
from persistence.repositories import SQLAlchemyHumanAccountRepository

from .query import GetUserAccountQuery
from .result import UserAccountDetails


class GetUserAccountHandler:
    """Load only an ordinary-user account through a bounded safe contract."""

    __slots__ = ("_human_account_repository",)

    def __init__(self, human_account_repository: SQLAlchemyHumanAccountRepository) -> None:
        self._human_account_repository = human_account_repository

    async def execute(self, query: GetUserAccountQuery) -> UserAccountDetails:
        """Return safe ordinary-user fields without exposing staff or credential state."""
        username = canonicalize_username(query.username)
        account = await self._human_account_repository.get_user_by_username(username)
        if account is None:
            raise UserAccountNotFound
        return UserAccountDetails(
            id=account.principal_id,
            username=account.username,
            nickname=account.nickname,
            status=account.principal.status,
            created_at=account.created_at,
        )

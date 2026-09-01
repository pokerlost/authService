"""Authorization principal command repository port."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from domain.authorization_principal import AuthorizationPrincipal


class AuthorizationPrincipalRepository(Protocol):
    """Persist and retrieve authorization principal aggregates."""

    async def add(self, principal: AuthorizationPrincipal) -> None:
        """Stage one new aggregate in the request-owned transaction."""
        ...

    async def get_by_principal_id(
        self,
        principal_id: UUID,
    ) -> AuthorizationPrincipal | None:
        """Return the aggregate with the exact principal identifier."""
        ...

    async def get_human_by_account_id(
        self,
        account_id: UUID,
    ) -> AuthorizationPrincipal | None:
        """Return the human aggregate bound to the exact account identifier."""
        ...

    async def get_service_by_service_slug(
        self,
        service_slug: str,
    ) -> AuthorizationPrincipal | None:
        """Return the service aggregate bound to the exact service slug."""
        ...

    async def save(self, principal: AuthorizationPrincipal) -> None:
        """Persist one validated aggregate mutation without completing the transaction."""
        ...

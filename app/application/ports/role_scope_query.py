"""Authorization role and OAuth2 scope query port."""

from __future__ import annotations

from collections.abc import Collection
from typing import Protocol

from pypokerlost.contracts.authorization import AuthorizationRole
from pypokerlost.types import OAuthScope

from domain.authorization_role_definition import AuthorizationRoleDefinition
from domain.oauth_scope_definition import OAuthScopeDefinition


class RoleScopeQuery(Protocol):
    """Read persisted role compatibility and exact explicit scope grants."""

    async def get_role_by_code(self, code: AuthorizationRole) -> AuthorizationRoleDefinition:
        """Return the persisted role with the exact code."""
        ...

    async def get_scopes_by_exact_names(
        self,
        names: Collection[OAuthScope],
    ) -> tuple[OAuthScopeDefinition, ...]:
        """Return every requested catalog scope or fail when any exact name is absent."""
        ...

    async def resolve_allowed_scope_names(
        self,
        role: AuthorizationRole,
    ) -> frozenset[OAuthScope]:
        """Return names from every explicit grant row for the exact role."""
        ...

    async def resolve_default_scope_names(
        self,
        role: AuthorizationRole,
    ) -> frozenset[OAuthScope]:
        """Return names from explicit default grant rows for the exact role."""
        ...

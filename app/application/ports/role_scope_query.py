"""Authorization role and OAuth2 scope query port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection

from domain.authorization_role import AuthorizationRole
from domain.enums import RoleCode
from domain.oauth_scope import OAuthScope
from domain.scope_name import ScopeName


class RoleScopeQuery(ABC):
    """Read persisted role compatibility and exact explicit scope grants."""

    @abstractmethod
    async def get_role_by_code(self, code: RoleCode) -> AuthorizationRole:
        """Return the persisted role with the exact code."""
        raise NotImplementedError

    @abstractmethod
    async def get_scopes_by_exact_names(
        self,
        names: Collection[ScopeName],
    ) -> tuple[OAuthScope, ...]:
        """Return every requested catalog scope or fail when any exact name is absent."""
        raise NotImplementedError

    @abstractmethod
    async def resolve_allowed_scope_names(self, role: RoleCode) -> frozenset[ScopeName]:
        """Return names from every explicit grant row for the exact role."""
        raise NotImplementedError

    @abstractmethod
    async def resolve_default_scope_names(self, role: RoleCode) -> frozenset[ScopeName]:
        """Return names from explicit default grant rows for the exact role."""
        raise NotImplementedError

"""Explicit OAuth2 scope grant application facade."""

from __future__ import annotations

from .grant_role_scope import GrantRoleScopeCommand, GrantRoleScopeHandler
from .grant_service_scope import GrantServiceScopeCommand, GrantServiceScopeHandler
from .list_role_scopes import ListRoleScopesHandler, ListRoleScopesQuery
from .list_service_scopes import ListServiceScopesHandler, ListServiceScopesQuery
from .revoke_role_scope import RevokeRoleScopeCommand, RevokeRoleScopeHandler
from .revoke_service_scope import RevokeServiceScopeCommand, RevokeServiceScopeHandler

__all__ = (
    "GrantRoleScopeCommand",
    "GrantRoleScopeHandler",
    "GrantServiceScopeCommand",
    "GrantServiceScopeHandler",
    "ListRoleScopesHandler",
    "ListRoleScopesQuery",
    "ListServiceScopesHandler",
    "ListServiceScopesQuery",
    "RevokeRoleScopeCommand",
    "RevokeRoleScopeHandler",
    "RevokeServiceScopeCommand",
    "RevokeServiceScopeHandler",
)

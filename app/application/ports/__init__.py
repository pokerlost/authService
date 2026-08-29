"""Focused application persistence port facade."""

from __future__ import annotations

from .authorization_principal_repository import AuthorizationPrincipalRepository
from .role_scope_query import RoleScopeQuery

__all__ = (
    "AuthorizationPrincipalRepository",
    "RoleScopeQuery",
)

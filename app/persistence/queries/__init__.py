"""Focused persistence query adapter facade."""

from __future__ import annotations

from .client_credentials_query import SQLAlchemyClientCredentialsQuery
from .role_scope_query import SQLAlchemyRoleScopeQuery

__all__ = (
    "SQLAlchemyClientCredentialsQuery",
    "SQLAlchemyRoleScopeQuery",
)

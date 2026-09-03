"""Focused persistence query adapter facade."""

from __future__ import annotations

from .client_credentials_query import SQLAlchemyClientCredentialsQuery
from .scope_definition_query import SQLAlchemyScopeDefinitionQuery

__all__ = (
    "SQLAlchemyClientCredentialsQuery",
    "SQLAlchemyScopeDefinitionQuery",
)

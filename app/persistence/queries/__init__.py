"""Optimized typed read-query facade."""

from __future__ import annotations

from .audit_events import SQLAlchemyAuditEventQuery
from .openapi_registry import SQLAlchemyOpenAPIRegistryQuery
from .scopes import SQLAlchemyScopeQuery

__all__ = (
    "SQLAlchemyAuditEventQuery",
    "SQLAlchemyOpenAPIRegistryQuery",
    "SQLAlchemyScopeQuery",
)

"""Authenticated human principal context."""

from __future__ import annotations

from uuid import UUID

from domain.enums import Role
from domain.value_model import ValueModel


class AuthenticatedHumanPrincipal(ValueModel):
    """Minimal trusted context for one active human session."""

    principal_id: UUID
    session_id: UUID
    role: Role
    scopes: frozenset[str]

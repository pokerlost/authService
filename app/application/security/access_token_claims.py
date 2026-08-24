"""Verified access-token claims used by application authentication."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.enums import Role
from domain.value_model import ValueModel


class AccessTokenClaims(ValueModel):
    """Minimal trusted identity and session claims from one access JWT."""

    principal_id: UUID
    session_id: UUID
    role: Role
    token_id: UUID
    issued_at: datetime
    expires_at: datetime
    scopes: frozenset[str]

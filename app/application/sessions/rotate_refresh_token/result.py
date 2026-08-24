"""Refresh-token rotation result."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from application.security import IssuedSessionTokens
from domain.enums import RefreshRotationStatus, Role


@dataclass(frozen=True, slots=True)
class RefreshRotationResult:
    """Commit-safe non-exceptional refresh-token rotation outcome."""

    status: RefreshRotationStatus
    tokens: IssuedSessionTokens | None = field(default=None, repr=False)
    principal_id: UUID | None = None
    session_id: UUID | None = None
    role: Role | None = None

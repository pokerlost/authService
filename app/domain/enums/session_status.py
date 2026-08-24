"""Persisted human session status."""

from __future__ import annotations

from enum import StrEnum


class SessionStatus(StrEnum):
    """Explicit revocation state independent from timestamp expiration."""

    ACTIVE = "active"
    REVOKED = "revoked"

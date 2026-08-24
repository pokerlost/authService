"""Persisted service credential revocation status."""

from __future__ import annotations

from enum import StrEnum


class ServiceCredentialStatus(StrEnum):
    """Explicit service credential state independent from expiration."""

    ACTIVE = "active"
    REVOKED = "revoked"

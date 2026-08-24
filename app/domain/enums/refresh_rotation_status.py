"""Refresh-token rotation application outcome."""

from __future__ import annotations

from enum import StrEnum


class RefreshRotationStatus(StrEnum):
    """Non-exceptional outcomes of refresh credential processing."""

    SUCCESS = "success"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    REUSE_DETECTED = "reuse_detected"
    INVALID_SCOPE = "invalid_scope"

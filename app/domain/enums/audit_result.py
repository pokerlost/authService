"""Durable security audit result."""

from __future__ import annotations

from enum import StrEnum


class AuditResult(StrEnum):
    """Outcome recorded for one security audit event."""

    SUCCESS = "success"
    FAILURE = "failure"

"""Persisted authorization role code."""

from __future__ import annotations

from enum import StrEnum


class RoleCode(StrEnum):
    """Closed persisted role codes without an unauthenticated category."""

    USER = "user"
    SUPPORT = "support"
    MASTER = "master"
    AUTO = "auto"

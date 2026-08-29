"""Authorization principal category."""

from __future__ import annotations

from enum import StrEnum


class PrincipalType(StrEnum):
    """Closed authorization principal categories."""

    HUMAN = "human"
    SERVICE = "service"

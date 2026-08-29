"""Authorization principal lifecycle status."""

from __future__ import annotations

from enum import StrEnum


class PrincipalStatus(StrEnum):
    """Closed authorization principal statuses."""

    ACTIVE = "active"
    DISABLED = "disabled"

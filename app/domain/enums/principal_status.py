"""Principal authentication status."""

from __future__ import annotations

from enum import StrEnum


class PrincipalStatus(StrEnum):
    """Whether a principal may authenticate."""

    ACTIVE = "active"
    DISABLED = "disabled"

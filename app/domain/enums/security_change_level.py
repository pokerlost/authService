"""OpenAPI authorization diff security classification."""

from __future__ import annotations

from enum import StrEnum


class SecurityChangeLevel(StrEnum):
    """Finite security effect of a normalized contract change."""

    NONE = "none"
    TIGHTENING = "tightening"
    WEAKENING = "weakening"
    BREAKING = "breaking"

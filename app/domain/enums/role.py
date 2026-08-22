"""Direct principal authorization role."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """Single direct PokerLost principal role without inheritance."""

    USER = "user"
    SUPPORT = "support"
    MASTER = "master"
    AUTO = "auto"

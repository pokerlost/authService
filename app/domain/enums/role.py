"""Direct principal identity classification."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """Single direct PokerLost principal class used to resolve explicit scope grants."""

    USER = "user"
    SUPPORT = "support"
    MASTER = "master"
    AUTO = "auto"

    @property
    def is_human(self) -> bool:
        """Report whether this role may own a human account and session."""
        return self in (Role.USER, Role.SUPPORT, Role.MASTER)

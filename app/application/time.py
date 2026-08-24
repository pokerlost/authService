"""UTC time source for application security operations."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

type UtcClock = Callable[[], datetime]


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)

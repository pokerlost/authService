"""Canonical PokerLost service slug."""

from __future__ import annotations

import re
from typing import Annotated, Final

from pydantic import BeforeValidator

_SERVICE_SLUG_PATTERN: Final = re.compile(r"[a-z0-9-]{2,63}\Z")


def validate_service_slug(value: object) -> str:
    """Require a canonical lowercase ASCII PokerLost service slug."""
    if not isinstance(value, str) or _SERVICE_SLUG_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "Service slug must contain 2 to 63 lowercase ASCII letters, digits, or hyphens"
        )
    return value


type ServiceSlug = Annotated[str, BeforeValidator(validate_service_slug)]

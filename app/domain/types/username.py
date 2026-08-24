"""Canonical human authentication username."""

from __future__ import annotations

import re
from typing import Annotated, Final

from pydantic import BeforeValidator

_USERNAME_PATTERN: Final = re.compile(r"[a-z0-9_]{3,32}\Z")


def canonicalize_username(value: object) -> str:
    """Strip, lowercase, and validate one ASCII authentication username."""
    if not isinstance(value, str):
        raise ValueError("Username must be a string")
    username = value.strip().lower()
    if _USERNAME_PATTERN.fullmatch(username) is None:
        raise ValueError("Username must contain 3 to 32 ASCII letters, digits, or underscores")
    return username


type Username = Annotated[str, BeforeValidator(canonicalize_username)]

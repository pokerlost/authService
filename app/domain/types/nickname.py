"""Bounded human display nickname."""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator


def normalize_nickname(value: object) -> str:
    """Strip and validate one non-empty Unicode display nickname."""
    if not isinstance(value, str):
        raise ValueError("Nickname must be a string")
    nickname = value.strip()
    if not 1 <= len(nickname) <= 64:
        raise ValueError("Nickname must contain 1 to 64 characters")
    return nickname


type Nickname = Annotated[str, BeforeValidator(normalize_nickname)]

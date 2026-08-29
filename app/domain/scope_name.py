"""Validated OAuth2 scope name value."""

from __future__ import annotations

import re
from typing import ClassVar, Self

from pydantic import field_validator
from pydantic_core import PydanticCustomError

from .value_model import ValueModel


class ScopeName(ValueModel):
    """Exact lowercase dotted OAuth2 scope identifier."""

    pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$",
    )

    value: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str) -> str:
        """Reject malformed, wildcard, uppercase, or single-segment names."""
        if cls.pattern.fullmatch(value) is None:
            raise PydanticCustomError(
                "invalid_scope_name",
                "OAuth2 scope name must be a lowercase dotted identifier",
            )
        return value

    @classmethod
    def parse(cls, value: str) -> Self:
        """Build a validated scope name without normalizing input."""
        return cls(value=value)

    def __str__(self) -> str:
        """Return the exact persisted scope identifier."""
        return self.value

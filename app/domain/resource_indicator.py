"""Exact OAuth2 resource indicator value."""

from __future__ import annotations

import re
from typing import ClassVar, Self

from pydantic import field_validator
from pydantic_core import PydanticCustomError

from domain.value_model import ValueModel


class ResourceIndicator(ValueModel):
    """Exact Pokerlost service resource URI without normalization."""

    pattern: ClassVar[re.Pattern[str]] = re.compile(
        r"^urn:pokerlost:service:[a-z][A-Za-z0-9]*$",
    )

    value: str

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: str) -> str:
        """Reject malformed, wildcard, or non-canonical service resources."""
        if cls.pattern.fullmatch(value) is None:
            raise PydanticCustomError(
                "invalid_resource_indicator",
                "Resource must be an exact Pokerlost service URI",
            )
        return value

    @classmethod
    def parse(cls, value: str) -> Self:
        """Build a validated resource without changing its value."""
        return cls(value=value)

    def __str__(self) -> str:
        """Return the exact resource URI."""
        return self.value

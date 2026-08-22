"""Immutable internal structured value base."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ValueModel(BaseModel):
    """Strict immutable alias-free application and domain value."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
        validate_default=True,
    )

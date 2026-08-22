"""Shared public API model configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class APIModel(BaseModel):
    """Strict camelCase public API model."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="forbid",
        hide_input_in_errors=True,
        populate_by_name=True,
        serialize_by_alias=True,
        validate_default=True,
    )

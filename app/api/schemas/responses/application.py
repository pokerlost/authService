"""Shared public application response envelope."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApplicationResponse[ResultT](BaseModel):
    """Single success and failure envelope for every public operation."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="forbid",
        populate_by_name=True,
    )

    ok: bool = Field(description="Whether the operation completed successfully.")
    result: ResultT | None = Field(default=None, description="Typed successful operation result.")
    error: str | None = Field(default=None, description="Stable machine-readable error code.")
    error_message: str | None = Field(default=None, description="Safe public error message.")
    request_id: UUID | None = Field(
        default=None,
        description="Server-generated request identifier for a failed operation.",
    )

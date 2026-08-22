"""Validated request context carried across API infrastructure."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field


class RequestContext(BaseModel):
    """Server-owned identifiers for one HTTP request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    request_id: UUID = Field(description="Server-generated request identifier.")
    correlation_id: str = Field(min_length=1, max_length=128)


def get_request_context(request: Request) -> RequestContext:
    """Return the context installed by request middleware."""
    context = request.state.request_context
    if not isinstance(context, RequestContext):
        raise RuntimeError("Request context is not initialized")
    return context

"""Safe human session response schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.enums import SessionStatus


class SessionResponse(ResponseModel):
    """Owned human session state without refresh-family internals."""

    id: UUID = Field(description="SessionModel identifier.")
    status: SessionStatus = Field(description="Persisted session revocation state.")
    created_at: datetime = Field(description="SessionModel creation time in UTC.")
    last_refreshed_at: datetime = Field(description="Last successful refresh time in UTC.")
    idle_expires_at: datetime = Field(description="Current idle expiration time in UTC.")
    absolute_expires_at: datetime = Field(description="Immutable absolute expiration time in UTC.")
    revoked_at: datetime | None = Field(description="Explicit revocation time in UTC.")
    current: bool = Field(description="Whether this is the access token's current session.")

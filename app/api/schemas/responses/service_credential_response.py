"""One-time service credential response schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from api.schemas.base import ResponseModel


class ServiceCredentialResponse(ResponseModel):
    """Public locator and intentionally disclosed one-time raw client secret."""

    client_id: str
    client_secret: str = Field(repr=False)
    expires_at: datetime

"""Support-safe ordinary-user account response schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.enums import PrincipalStatus


class SupportUserAccountResponse(ResponseModel):
    """Minimal ordinary-user identity and status exposed to authorized staff."""

    id: UUID = Field(description="Ordinary-user authentication principal identifier.")
    username: str = Field(description="Canonical ordinary-user login identifier.")
    nickname: str = Field(description="Ordinary-user display name.")
    status: PrincipalStatus = Field(description="Current account authentication status.")
    created_at: datetime = Field(description="Account creation timestamp.")

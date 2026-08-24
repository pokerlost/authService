"""Safe human account response schema."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.enums import Role


class AccountResponse(ResponseModel):
    """Minimal human account identity safe for public responses."""

    id: UUID = Field(description="Authentication principal identifier.")
    username: str = Field(description="Canonical human login identifier.")
    nickname: str = Field(description="Non-unique human display name.")
    role: Role = Field(description="Single direct identity role classification.")

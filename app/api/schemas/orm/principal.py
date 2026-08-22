"""Public principal metadata schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from api.schemas.base import ORMSchema
from domain.enums import PrincipalStatus, Role


class PrincipalSchema(ORMSchema):
    """Safe public principal metadata."""

    id: UUID = Field(description="Principal identifier.")
    role: Role = Field(description="Single direct authorization role.")
    status: PrincipalStatus = Field(description="Current principal authentication status.")
    created_at: datetime = Field(description="UTC creation timestamp.")
    updated_at: datetime = Field(description="UTC last-update timestamp.")

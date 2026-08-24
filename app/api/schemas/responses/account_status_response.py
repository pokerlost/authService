"""Human account status response schema."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.enums import PrincipalStatus


class AccountStatusResponse(ResponseModel):
    """Safe result of one human account status transition."""

    principal_id: UUID = Field(description="Human authentication principal identifier.")
    status: PrincipalStatus = Field(description="Current account authentication status.")

"""Human account status control request."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import APIModel


class AccountStatusRequest(APIModel):
    """Target human principal for one master-controlled status transition."""

    principal_id: UUID = Field(description="Target human authentication principal identifier.")

"""Master-assisted human password reset request."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import APIModel
from domain.types import PasswordValue


class ResetHumanPasswordRequest(APIModel):
    """Human target and operator-supplied replacement password."""

    principal_id: UUID = Field(description="Target human principal identifier.")
    new_password: PasswordValue = Field(repr=False)

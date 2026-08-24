"""Authenticated password change request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from domain.types import PasswordValue


class ChangePasswordRequest(APIModel):
    """Current and replacement password supplied by the authenticated human."""

    current_password: PasswordValue = Field(repr=False)
    new_password: PasswordValue = Field(repr=False)

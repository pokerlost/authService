"""Staff human account creation request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from domain.types import Nickname, PasswordValue, Username


class CreateStaffAccountRequest(APIModel):
    """Validated staff identity and password without client-controlled role or status."""

    username: Username = Field(description="Canonical human login identifier.")
    nickname: Nickname = Field(description="Non-unique human display name.")
    password: PasswordValue = Field(description="New staff account password.", repr=False)

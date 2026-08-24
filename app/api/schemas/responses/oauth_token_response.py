"""Unified OAuth2 token response."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from api.schemas.base import ResponseModel


class OAuthTokenResponse(ResponseModel):
    """Standard OAuth2 token meanings inside the PokerLost response envelope."""

    access_token: str = Field(alias="access_token", repr=False)
    token_type: Literal["Bearer"] = Field(alias="token_type")
    expires_in: int = Field(alias="expires_in", ge=1)
    scope: str
    refresh_token: str | None = Field(default=None, alias="refresh_token", repr=False)

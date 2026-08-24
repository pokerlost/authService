"""Unified OAuth2 token form request."""

from __future__ import annotations

from pydantic import Field, SecretStr

from api.schemas.base import APIModel


class OAuthTokenRequest(APIModel):
    """OAuth2-compatible form values for all PokerLost v1 token grants."""

    grant_type: str = Field(alias="grant_type", min_length=1, max_length=64)
    username: str | None = Field(default=None, max_length=256)
    password: SecretStr | None = Field(default=None, max_length=1_024, repr=False)
    refresh_token: SecretStr | None = Field(
        default=None,
        alias="refresh_token",
        max_length=2_048,
        repr=False,
    )
    scope: str | None = Field(default=None, max_length=65_536)
    resource: str | None = Field(default=None, max_length=128)

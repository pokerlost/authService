"""OAuth2 access-token success response schema."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from api.schemas.base import ResponseModel


class OAuthTokenResponse(ResponseModel):
    """Bearer access-token result carried by the PokerLost application envelope."""

    access_token: str = Field(
        repr=False,
        min_length=1,
        description="Compact signed access token.",
    )
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(ge=1, description="Access-token lifetime in seconds.")
    scope: str = Field(description="Sorted exact granted OAuth2 scope set.")

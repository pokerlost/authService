"""OAuth2 token form request schema."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, WithJsonSchema

from api.schemas.base import RequestModel


class OAuthTokenRequest(RequestModel):
    """Typed form fields accepted by the OAuth2 token operation."""

    grant_type: Annotated[
        tuple[str, ...],
        WithJsonSchema({"type": "string"}),
    ] = Field(description="Requested OAuth2 grant type.")
    scope: Annotated[
        tuple[str, ...],
        WithJsonSchema({"type": "string"}),
    ] = Field(
        description="Space-delimited requested OAuth2 scope names.",
    )
    resource: Annotated[
        tuple[str, ...],
        WithJsonSchema({"type": "string"}),
    ] = Field(description="Exact OAuth2 resource indicator.")

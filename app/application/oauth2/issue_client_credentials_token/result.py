"""Client-credentials token issuance result."""

from __future__ import annotations

from pydantic import Field, SecretStr
from pypokerlost.enums import PokerlostScopes
from pypokerlost.types import PokerlostAudience

from application import Result


class IssueClientCredentialsTokenResult(Result):
    """Signed access token and its exact granted response metadata."""

    access_token: SecretStr = Field(repr=False, min_length=1)
    expires_in: int
    scopes: tuple[PokerlostScopes, ...]
    audience: PokerlostAudience

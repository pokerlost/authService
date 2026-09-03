"""Client-credentials token issuance command."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field, SecretStr
from pypokerlost.enums import PokerlostScopes
from pypokerlost.types import PokerlostAudience

from application import Command


class IssueClientCredentialsTokenCommand(Command):
    """Already parsed protocol input for service-token issuance."""

    client_id: UUID
    client_secret: SecretStr = Field(repr=False)
    requested_scopes: tuple[PokerlostScopes, ...]
    audience: PokerlostAudience

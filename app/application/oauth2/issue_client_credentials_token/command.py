"""Client-credentials token issuance command."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field, SecretStr
from pypokerlost.types import OAuthScope

from application import Command
from domain.resource_indicator import ResourceIndicator


class IssueClientCredentialsTokenCommand(Command):
    """Already parsed protocol input for service-token issuance."""

    client_id: UUID
    client_secret: SecretStr = Field(repr=False)
    requested_scopes: tuple[OAuthScope, ...]
    resource: ResourceIndicator

"""Issue AUTO service token command."""

from __future__ import annotations

from pydantic import Field, SecretStr

from domain.types import ServiceSlug
from domain.value_model import ValueModel


class IssueServiceTokenCommand(ValueModel):
    """Client credential and exact target audience supplied by a service."""

    client_id: str = Field(min_length=1, max_length=128)
    client_secret: SecretStr = Field(max_length=1024, repr=False)
    audience: ServiceSlug
    requested_scope: str | None = None

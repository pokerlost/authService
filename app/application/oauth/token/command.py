"""Unified OAuth2 token grant command."""

from __future__ import annotations

from pydantic import Field, SecretStr

from application.audit import AuditContext
from domain.value_model import ValueModel


class OAuthTokenCommand(ValueModel):
    """Secret-aware values accepted by the PokerLost OAuth2 token profile."""

    grant_type: str = Field(min_length=1, max_length=64)
    username: str | None = Field(default=None, max_length=256)
    password: SecretStr | None = Field(default=None, max_length=1_024, repr=False)
    refresh_token: SecretStr | None = Field(default=None, max_length=2_048, repr=False)
    scope: str | None = Field(default=None, max_length=65_536)
    resource: str | None = Field(default=None, max_length=128)
    client_id: str | None = Field(default=None, max_length=128)
    client_secret: SecretStr | None = Field(default=None, max_length=1_024, repr=False)
    audit_context: AuditContext

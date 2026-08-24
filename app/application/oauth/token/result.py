"""Unified OAuth2 token grant result."""

from __future__ import annotations

from pydantic import Field

from domain.enums import OAuthTokenStatus
from domain.value_model import ValueModel


class OAuthTokenResult(ValueModel):
    """Commit-safe token result or stable non-exceptional grant failure."""

    status: OAuthTokenStatus
    access_token: str | None = Field(default=None, repr=False)
    refresh_token: str | None = Field(default=None, repr=False)
    expires_in: int | None = None
    scopes: frozenset[str] = Field(default_factory=frozenset)

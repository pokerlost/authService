"""Unified OAuth2 token endpoint application outcome."""

from __future__ import annotations

from enum import StrEnum


class OAuthTokenStatus(StrEnum):
    """Finite grant outcome mapped to the PokerLost ApplicationResponse profile."""

    SUCCESS = "success"
    INVALID_GRANT = "invalid_grant"
    INVALID_CLIENT = "invalid_client"
    INVALID_SCOPE = "invalid_scope"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"
    RATE_LIMITED = "rate_limited"

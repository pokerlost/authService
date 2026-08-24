"""OAuth2 invalid grant error."""

from __future__ import annotations

from .base import AuthenticationError


class InvalidOAuthGrant(AuthenticationError):
    """Supplied OAuth2 resource-owner or refresh grant is unusable."""

    error_code = "AUTH_OAUTH_INVALID_GRANT"
    public_message = "OAuth2 grant is invalid."

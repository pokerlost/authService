"""OAuth2 invalid client error."""

from __future__ import annotations

from .base import AuthenticationError


class InvalidOAuthClient(AuthenticationError):
    """Supplied OAuth2 client authentication is unusable."""

    error_code = "AUTH_OAUTH_INVALID_CLIENT"
    public_message = "OAuth2 client authentication failed."

"""OAuth2 unsupported grant type error."""

from __future__ import annotations

from application.errors.base import ApplicationError


class UnsupportedOAuthGrantType(ApplicationError):
    """Requested OAuth2 grant type is outside the PokerLost v1 profile."""

    error_code = "AUTH_OAUTH_UNSUPPORTED_GRANT_TYPE"
    public_message = "OAuth2 grant type is unsupported."

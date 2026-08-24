"""OAuth2 invalid requested scope error."""

from __future__ import annotations

from application.errors.base import ApplicationError


class InvalidOAuthScope(ApplicationError):
    """Requested OAuth2 scope is malformed, unknown, or not explicitly granted."""

    error_code = "AUTH_OAUTH_INVALID_SCOPE"
    public_message = "Requested OAuth2 scope is invalid."

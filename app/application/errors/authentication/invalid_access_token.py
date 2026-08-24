"""Generic invalid access-token error."""

from __future__ import annotations

from .base import AuthenticationError


class InvalidAccessToken(AuthenticationError):
    """Access credential cannot establish a valid authenticated context."""

    error_code = "AUTH_INVALID_ACCESS_TOKEN"
    public_message = "Invalid access token."

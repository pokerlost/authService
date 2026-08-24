"""Generic invalid refresh-token error."""

from __future__ import annotations

from .base import AuthenticationError


class InvalidRefreshToken(AuthenticationError):
    """Refresh credential is invalid or cannot be used."""

    error_code = "AUTH_INVALID_REFRESH_TOKEN"
    public_message = "Invalid refresh token."

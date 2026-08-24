"""Generic invalid human credential error."""

from __future__ import annotations

from .base import AuthenticationError


class InvalidCredentials(AuthenticationError):
    """Human login credentials are invalid or unusable."""

    error_code = "AUTH_INVALID_CREDENTIALS"
    public_message = "Invalid credentials."

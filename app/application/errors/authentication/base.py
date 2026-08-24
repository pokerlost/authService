"""Application authentication error category."""

from __future__ import annotations

from application.errors.base import ApplicationError


class AuthenticationError(ApplicationError):
    """Supplied authentication credentials cannot establish an identity."""

    error_code = "AUTH_AUTHENTICATION_FAILED"
    public_message = "Authentication failed."

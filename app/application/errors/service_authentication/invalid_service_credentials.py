"""Generic invalid AUTO service credential error."""

from __future__ import annotations

from application.errors.authentication.base import AuthenticationError


class InvalidServiceCredentials(AuthenticationError):
    """Service credentials or requested audience cannot establish machine identity."""

    error_code = "AUTH_INVALID_SERVICE_CREDENTIALS"
    public_message = "Invalid service credentials."

"""AUTO service credential not-found error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class ServiceCredentialNotFound(NotFoundError):
    """Requested public service credential identifier does not exist."""

    error_code = "AUTH_SERVICE_CREDENTIAL_NOT_FOUND"
    public_message = "Service credential not found."

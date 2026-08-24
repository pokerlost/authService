"""AUTO service principal not-found error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class ServicePrincipalNotFound(NotFoundError):
    """Requested canonical service identity does not exist."""

    error_code = "AUTH_SERVICE_PRINCIPAL_NOT_FOUND"
    public_message = "Service principal not found."

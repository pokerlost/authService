"""Duplicate AUTO service principal error."""

from __future__ import annotations

from application.errors.conflict import ConflictError


class ServicePrincipalAlreadyExists(ConflictError):
    """Canonical service slug already belongs to an AUTO principal."""

    error_code = "AUTH_SERVICE_PRINCIPAL_ALREADY_EXISTS"
    public_message = "Service principal already exists."

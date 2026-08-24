"""OpenAPI contract registration identity error."""

from __future__ import annotations

from application.errors.invalid_operation import InvalidOperationError


class OpenAPIContractRegistrationInvalidError(InvalidOperationError):
    """Submitted JSON lacks bounded identity facts required for persistence."""

    error_code = "AUTH_OPENAPI_CONTRACT_REGISTRATION_INVALID"
    public_message = "OpenAPI document cannot be registered."

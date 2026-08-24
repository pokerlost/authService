"""Global OpenAPI operation identity ownership conflict."""

from __future__ import annotations

from application.errors.conflict import ConflictError


class OpenAPIOperationIDConflictError(ConflictError):
    """Candidate operation identity is permanently owned by another service."""

    error_code = "AUTH_OPENAPI_OPERATION_ID_CONFLICT"
    public_message = "OpenAPI operation ID is owned by another service."

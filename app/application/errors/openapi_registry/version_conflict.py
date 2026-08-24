"""Immutable OpenAPI contract version conflict."""

from __future__ import annotations

from application.errors.conflict import ConflictError


class OpenAPIContractVersionConflictError(ConflictError):
    """One service version already names a different schema hash."""

    error_code = "AUTH_OPENAPI_CONTRACT_VERSION_CONFLICT"
    public_message = "OpenAPI contract version already identifies a different document."

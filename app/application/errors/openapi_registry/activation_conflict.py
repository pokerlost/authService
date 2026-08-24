"""OpenAPI activation optimistic concurrency conflict."""

from __future__ import annotations

from application.errors.conflict import ConflictError


class OpenAPIContractActivationConflictError(ConflictError):
    """Active base, diff, or safe transition no longer matches the request."""

    error_code = "AUTH_OPENAPI_CONTRACT_ACTIVATION_CONFLICT"
    public_message = "OpenAPI contract activation conflicts with current registry state."

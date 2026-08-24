"""OpenAPI contract not found error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class OpenAPIContractNotFoundError(NotFoundError):
    """Requested immutable OpenAPI contract does not exist."""

    error_code = "AUTH_OPENAPI_CONTRACT_NOT_FOUND"
    public_message = "OpenAPI contract not found."

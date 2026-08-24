"""OpenAPI contract not validated error."""

from __future__ import annotations

from application.errors.conflict import ConflictError


class OpenAPIContractNotValidatedError(ConflictError):
    """Requested lifecycle operation requires successful prior validation."""

    error_code = "AUTH_OPENAPI_CONTRACT_NOT_VALIDATED"
    public_message = "OpenAPI contract has not been validated."

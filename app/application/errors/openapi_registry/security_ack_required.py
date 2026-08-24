"""OpenAPI security-change acknowledgement required error."""

from __future__ import annotations

from application.errors.conflict import ConflictError


class OpenAPIContractSecurityAcknowledgementRequiredError(ConflictError):
    """Activation explicitly omitted acknowledgement of a security-significant diff."""

    error_code = "AUTH_OPENAPI_CONTRACT_SECURITY_ACK_REQUIRED"
    public_message = "OpenAPI security changes require explicit acknowledgement."

"""OpenAPI contract validation response schemas."""

from __future__ import annotations

from api.schemas.base import ResponseModel
from application.openapi_registry import OpenAPIValidationIssueCode


class ValidationIssueResponse(ResponseModel):
    """One safe stable issue without raw document fragments."""

    code: OpenAPIValidationIssueCode
    location: str
    message: str


class ValidationResponse(ResponseModel):
    """Finite fail-closed validation result."""

    valid: bool
    issues: list[ValidationIssueResponse]

"""OpenAPI contract registration request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from application.audit import AuditContext
from application.openapi_registry import RegisterOpenAPIContractCommand


class RegisterOpenAPIContractRequest(APIModel):
    """One OpenAPI JSON object with identity extracted server-side."""

    document: dict[str, object] = Field(
        description="OpenAPI 3.1 JSON object submitted without YAML or remote fetching."
    )

    def to_command(self, audit_context: AuditContext) -> RegisterOpenAPIContractCommand:
        """Map the submitted JSON object to immutable registration input."""
        return RegisterOpenAPIContractCommand(
            document=self.document,
            audit_context=audit_context,
        )

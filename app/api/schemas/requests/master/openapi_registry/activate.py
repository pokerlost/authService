"""OpenAPI contract activation request."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import APIModel
from application.audit import AuditContext
from application.openapi_registry import ActivateOpenAPIContractCommand


class ActivateOpenAPIContractRequest(APIModel):
    """Optimistic base and diff proof with explicit security acknowledgement."""

    contract_id: UUID = Field(description="Validated or retired candidate contract identifier.")
    expected_base_contract_id: UUID | None = Field(
        description="Active base observed when the candidate diff was calculated."
    )
    expected_diff_hash: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description="Canonical SHA-256 hash of the observed normalized diff.",
    )
    acknowledge_security_changes: bool = Field(
        description="Explicitly acknowledge a security-significant activation diff."
    )

    def to_command(self, audit_context: AuditContext) -> ActivateOpenAPIContractCommand:
        """Map optimistic activation input without deriving a new base."""
        return ActivateOpenAPIContractCommand(
            contract_id=self.contract_id,
            expected_base_contract_id=self.expected_base_contract_id,
            expected_diff_hash=self.expected_diff_hash,
            acknowledge_security_changes=self.acknowledge_security_changes,
            audit_context=audit_context,
        )

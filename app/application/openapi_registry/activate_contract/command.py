"""Activate validated OpenAPI contract command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class ActivateOpenAPIContractCommand(ValueModel):
    """Optimistic base and diff proof plus explicit security acknowledgement."""

    contract_id: UUID
    expected_base_contract_id: UUID | None
    expected_diff_hash: str
    acknowledge_security_changes: bool
    audit_context: AuditContext

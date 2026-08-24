"""Retire OpenAPI contract command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class RetireOpenAPIContractCommand(ValueModel):
    """Validated or active immutable contract selected for retirement."""

    contract_id: UUID
    audit_context: AuditContext

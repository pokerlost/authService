"""Validate registered OpenAPI contract command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class ValidateOpenAPIContractCommand(ValueModel):
    """Immutable contract selected for fail-closed validation."""

    contract_id: UUID
    audit_context: AuditContext

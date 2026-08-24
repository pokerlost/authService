"""Register immutable OpenAPI contract command."""

from __future__ import annotations

from application.audit import AuditContext
from domain.value_model import ValueModel


class RegisterOpenAPIContractCommand(ValueModel):
    """Submitted OpenAPI JSON object without duplicated identity fields."""

    document: dict[str, object]
    audit_context: AuditContext

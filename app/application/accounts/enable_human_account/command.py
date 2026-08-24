"""Human account enable command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class EnableHumanAccountCommand(ValueModel):
    """Target for one human account enable transition."""

    target_principal_id: UUID
    audit_context: AuditContext

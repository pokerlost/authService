"""Human account disable command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class DisableHumanAccountCommand(ValueModel):
    """Authenticated actor and target for one human account disable transition."""

    target_principal_id: UUID
    audit_context: AuditContext

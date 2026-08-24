"""Current-session revocation command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class RevokeCurrentSessionCommand(ValueModel):
    """Server-authenticated identity and current session to revoke."""

    principal_id: UUID
    session_id: UUID
    audit_context: AuditContext

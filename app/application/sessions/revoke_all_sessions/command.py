"""All-session revocation command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class RevokeAllSessionsCommand(ValueModel):
    """Authenticated principal whose active session families must be revoked."""

    principal_id: UUID
    audit_context: AuditContext

"""Owned-session revocation command."""

from __future__ import annotations

from uuid import UUID

from application.audit import AuditContext
from domain.value_model import ValueModel


class RevokeSessionCommand(ValueModel):
    """Authenticated owner and target session identifiers."""

    principal_id: UUID
    session_id: UUID
    audit_context: AuditContext

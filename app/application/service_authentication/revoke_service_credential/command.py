"""Revoke AUTO service credential command."""

from __future__ import annotations

from pydantic import Field

from application.audit import AuditContext
from domain.value_model import ValueModel


class RevokeServiceCredentialCommand(ValueModel):
    """Public random service credential identifier selected by an operator."""

    client_id: str = Field(min_length=1, max_length=128)
    audit_context: AuditContext

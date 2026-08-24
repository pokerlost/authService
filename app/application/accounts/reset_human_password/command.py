"""Master-assisted human password reset command."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from application.audit import AuditContext
from domain.types import PasswordValue
from domain.value_model import ValueModel


class ResetHumanPasswordCommand(ValueModel):
    """Human target and operator-supplied replacement password."""

    target_principal_id: UUID
    new_password: PasswordValue = Field(repr=False)
    audit_context: AuditContext

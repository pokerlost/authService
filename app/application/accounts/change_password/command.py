"""Authenticated password change command."""

from __future__ import annotations

from pydantic import Field

from application.audit import AuditContext
from domain.types import PasswordValue
from domain.value_model import ValueModel


class ChangePasswordCommand(ValueModel):
    """Current and replacement password for the authenticated human actor."""

    current_password: PasswordValue = Field(repr=False)
    new_password: PasswordValue = Field(repr=False)
    audit_context: AuditContext

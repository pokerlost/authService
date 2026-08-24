"""Trusted human account creation command."""

from __future__ import annotations

from pydantic import Field

from application.audit import AuditContext
from domain.enums import Role
from domain.types import Nickname, PasswordValue, Username
from domain.value_model import ValueModel


class CreateHumanAccountCommand(ValueModel):
    """Validated account values with a server-controlled direct human role."""

    username: Username
    nickname: Nickname
    password: PasswordValue = Field(repr=False)
    role: Role
    audit_context: AuditContext

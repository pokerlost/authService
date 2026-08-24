"""Ordinary-user registration command."""

from __future__ import annotations

from pydantic import Field

from application.audit import AuditContext
from domain.types import Nickname, PasswordValue, Username
from domain.value_model import ValueModel


class RegisterUserCommand(ValueModel):
    """Validated transport-independent ordinary-user registration values."""

    username: Username
    nickname: Nickname
    password: PasswordValue = Field(repr=False)
    audit_context: AuditContext

"""Ordinary-user registration request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from application.audit import AuditContext
from application.users import RegisterUserCommand
from domain.types import Nickname, PasswordValue, Username


class RegisterUserRequest(APIModel):
    """Validated public ordinary-user registration payload."""

    username: Username = Field(description="Canonical human login identifier.")
    nickname: Nickname = Field(description="Non-unique human display name.")
    password: PasswordValue = Field(description="New account password.", repr=False)

    def to_command(self, audit_context: AuditContext) -> RegisterUserCommand:
        """Map validated transport values to the registration command."""
        return RegisterUserCommand(
            username=self.username,
            nickname=self.nickname,
            password=self.password,
            audit_context=audit_context,
        )

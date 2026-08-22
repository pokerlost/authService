"""Ordinary-user registration request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import RequestModel
from application.users import RegisterUserCommand
from domain.types import EmailAddress, PasswordValue


class RegisterUserRequest(RequestModel):
    """Validated public ordinary-user registration payload."""

    email: EmailAddress = Field(description="Human account email address.")
    password: PasswordValue = Field(description="New account password.", repr=False)

    def to_command(self) -> RegisterUserCommand:
        """Map validated transport values to the registration command."""
        return RegisterUserCommand(email=self.email, password=self.password)

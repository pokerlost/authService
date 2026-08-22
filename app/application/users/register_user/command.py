"""Ordinary-user registration command."""

from __future__ import annotations

from pydantic import Field

from domain.types import EmailAddress, PasswordValue
from domain.value_model import ValueModel


class RegisterUserCommand(ValueModel):
    """Validated transport-independent registration values."""

    email: EmailAddress
    password: PasswordValue = Field(repr=False)

"""Human login command."""

from __future__ import annotations

from pydantic import Field

from domain.types import PasswordValue, Username
from domain.value_model import ValueModel


class LoginCommand(ValueModel):
    """Validated transport-independent human login credentials."""

    username: Username
    password: PasswordValue = Field(repr=False)
    requested_scope: str | None = None

"""Ordinary-user registration result."""

from __future__ import annotations

from uuid import UUID

from domain.enums import Role
from domain.value_model import ValueModel


class RegisterUserResult(ValueModel):
    """Safe account identity returned after registration."""

    id: UUID
    username: str
    nickname: str
    role: Role

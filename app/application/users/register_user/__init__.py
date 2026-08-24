"""Ordinary-user registration operation facade."""

from __future__ import annotations

from .command import RegisterUserCommand
from .handler import RegisterUserHandler
from .result import RegisterUserResult

__all__ = ("RegisterUserCommand", "RegisterUserHandler", "RegisterUserResult")

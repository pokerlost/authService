"""Ordinary-user registration operation facade."""

from __future__ import annotations

from .command import RegisterUserCommand
from .handler import RegisterUserHandler

__all__ = ("RegisterUserCommand", "RegisterUserHandler")

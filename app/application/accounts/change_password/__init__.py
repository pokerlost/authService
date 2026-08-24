"""Authenticated password change facade."""

from __future__ import annotations

from .command import ChangePasswordCommand
from .handler import ChangePasswordHandler

__all__ = ("ChangePasswordCommand", "ChangePasswordHandler")

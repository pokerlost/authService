"""Role scope grant operation facade."""

from __future__ import annotations

from .command import GrantRoleScopeCommand
from .handler import GrantRoleScopeHandler

__all__ = ("GrantRoleScopeCommand", "GrantRoleScopeHandler")

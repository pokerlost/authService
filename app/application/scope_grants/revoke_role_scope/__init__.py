"""Role scope revocation operation facade."""

from __future__ import annotations

from .command import RevokeRoleScopeCommand
from .handler import RevokeRoleScopeHandler

__all__ = ("RevokeRoleScopeCommand", "RevokeRoleScopeHandler")

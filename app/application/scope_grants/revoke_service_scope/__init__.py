"""Service scope revocation operation facade."""

from __future__ import annotations

from .command import RevokeServiceScopeCommand
from .handler import RevokeServiceScopeHandler

__all__ = ("RevokeServiceScopeCommand", "RevokeServiceScopeHandler")

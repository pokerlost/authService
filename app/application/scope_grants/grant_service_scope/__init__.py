"""Service scope grant operation facade."""

from __future__ import annotations

from .command import GrantServiceScopeCommand
from .handler import GrantServiceScopeHandler

__all__ = ("GrantServiceScopeCommand", "GrantServiceScopeHandler")

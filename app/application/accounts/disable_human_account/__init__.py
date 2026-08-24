"""Human account disable operation facade."""

from __future__ import annotations

from .command import DisableHumanAccountCommand
from .handler import DisableHumanAccountHandler

__all__ = ("DisableHumanAccountCommand", "DisableHumanAccountHandler")

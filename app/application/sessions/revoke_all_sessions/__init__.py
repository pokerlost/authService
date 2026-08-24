"""All-session revocation operation facade."""

from __future__ import annotations

from .command import RevokeAllSessionsCommand
from .handler import RevokeAllSessionsHandler

__all__ = ("RevokeAllSessionsCommand", "RevokeAllSessionsHandler")

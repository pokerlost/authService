"""Revoke AUTO service audience operation facade."""

from __future__ import annotations

from .command import RevokeServiceAudienceCommand
from .handler import RevokeServiceAudienceHandler

__all__ = ("RevokeServiceAudienceCommand", "RevokeServiceAudienceHandler")

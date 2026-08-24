"""Grant AUTO service audience operation facade."""

from __future__ import annotations

from .command import GrantServiceAudienceCommand
from .handler import GrantServiceAudienceHandler

__all__ = ("GrantServiceAudienceCommand", "GrantServiceAudienceHandler")

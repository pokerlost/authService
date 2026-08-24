"""Get authorization manifest operation facade."""

from __future__ import annotations

from .handler import GetAuthorizationManifestHandler
from .query import GetAuthorizationManifestQuery

__all__ = (
    "GetAuthorizationManifestHandler",
    "GetAuthorizationManifestQuery",
)

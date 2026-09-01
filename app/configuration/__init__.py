"""Typed service configuration facade."""

from __future__ import annotations

from .jwt import JWTSettings
from .oauth2 import OAuth2Settings
from .settings import Settings

__all__ = (
    "JWTSettings",
    "OAuth2Settings",
    "Settings",
)

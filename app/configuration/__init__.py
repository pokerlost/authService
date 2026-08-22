"""Typed service configuration facade."""

from __future__ import annotations

from .jwt import JWTSettings
from .settings import Settings

__all__ = ("JWTSettings", "Settings")

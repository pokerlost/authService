"""SQLAlchemy database foundation facade."""

from __future__ import annotations

from .base import Base
from .session import create_session_factory

__all__ = (
    "Base",
    "create_session_factory",
)

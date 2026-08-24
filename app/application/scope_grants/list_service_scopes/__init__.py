"""Service scope list operation facade."""

from __future__ import annotations

from .handler import ListServiceScopesHandler
from .query import ListServiceScopesQuery

__all__ = ("ListServiceScopesHandler", "ListServiceScopesQuery")

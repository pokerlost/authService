"""Support-safe ordinary-user lookup facade."""

from __future__ import annotations

from .handler import GetUserAccountHandler
from .query import GetUserAccountQuery
from .result import UserAccountDetails

__all__ = ("GetUserAccountHandler", "GetUserAccountQuery", "UserAccountDetails")

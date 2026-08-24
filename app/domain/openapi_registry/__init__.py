"""Normalized OpenAPI registry domain-value facade."""

from __future__ import annotations

from .normalized_authorization import NormalizedAuthorizationPolicy
from .normalized_operation import NormalizedAPIOperation

__all__ = (
    "NormalizedAPIOperation",
    "NormalizedAuthorizationPolicy",
)

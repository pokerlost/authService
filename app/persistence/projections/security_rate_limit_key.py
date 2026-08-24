"""Security rate-limit composite key projection."""

from __future__ import annotations

from domain.enums import RateLimitKind
from domain.value_model import ValueModel


class SecurityRateLimitKeyProjection(ValueModel):
    """One PostgreSQL-backed limiter row identity selected for cleanup."""

    kind: RateLimitKind
    key_fingerprint: str

"""PostgreSQL security rate-limit category."""

from __future__ import annotations

from enum import StrEnum


class RateLimitKind(StrEnum):
    """Authentication flow protected by one independent rate policy."""

    PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"

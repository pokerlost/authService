"""OAuth2 client category."""

from __future__ import annotations

from enum import StrEnum


class OAuthClientType(StrEnum):
    """Closed OAuth2 client categories."""

    PUBLIC = "public"
    CONFIDENTIAL = "confidential"

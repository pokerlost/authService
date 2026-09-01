"""OAuth2 client lifecycle status."""

from __future__ import annotations

from enum import StrEnum


class OAuthClientStatus(StrEnum):
    """Closed OAuth2 client statuses."""

    ACTIVE = "active"
    DISABLED = "disabled"

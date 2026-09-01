"""OAuth2 client credential lifecycle status."""

from __future__ import annotations

from enum import StrEnum


class OAuthClientCredentialStatus(StrEnum):
    """Closed OAuth2 client credential statuses."""

    ACTIVE = "active"
    RETIRING = "retiring"
    REVOKED = "revoked"

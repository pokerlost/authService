"""OAuth2 token issuance settings."""

from __future__ import annotations

from pydantic import Field, field_validator

from .base import SettingsModel


class OAuth2Settings(SettingsModel):
    """Required OAuth2 issuer and short-lived access-token policy."""

    issuer: str = Field(
        min_length=1,
        max_length=2048,
        description="Exact issuer copied into access-token claims.",
    )
    access_token_ttl_seconds: int = Field(
        default=600,
        ge=60,
        le=3600,
        description="Bounded service access-token lifetime in seconds.",
    )

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, issuer: str) -> str:
        """Reject blank or padded issuers without normalizing the claim value."""
        if not issuer.strip() or issuer != issuer.strip():
            raise ValueError(
                "OAuth2 issuer must be non-empty and must not contain outer whitespace"
            )
        return issuer

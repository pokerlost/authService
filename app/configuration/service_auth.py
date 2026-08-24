"""AUTO service authentication settings."""

from __future__ import annotations

from datetime import timedelta

from pydantic import Field, SecretStr

from .base import SettingsModel


class ServiceAuthSettings(SettingsModel):
    """Bounded machine token and service credential security configuration."""

    access_token_ttl_seconds: int = Field(
        default=300,
        ge=60,
        le=3_600,
        description="AUTO access-token TTL in seconds.",
    )
    credential_ttl_seconds: int = Field(
        default=7_776_000,
        ge=300,
        le=31_536_000,
        description="Finite lifetime assigned to newly created service credentials.",
    )
    credential_pepper: SecretStr = Field(
        min_length=32,
        max_length=1024,
        description="Dedicated HMAC pepper for service credential protection.",
        repr=False,
    )

    @property
    def credential_ttl(self) -> timedelta:
        """Return the configured service credential lifetime as timedelta."""
        return timedelta(seconds=self.credential_ttl_seconds)

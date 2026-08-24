"""Opaque refresh-token protection settings."""

from __future__ import annotations

from datetime import timedelta

from pydantic import Field, SecretStr

from .base import SettingsModel


class RefreshTokenSettings(SettingsModel):
    """Validated refresh lifetime and mandatory server-side HMAC pepper."""

    ttl_seconds: int = Field(default=604_800, ge=60, le=31_536_000)
    pepper: SecretStr = Field(min_length=32, max_length=1024, repr=False)

    @property
    def ttl(self) -> timedelta:
        """Return the refresh-token lifetime as timedelta."""
        return timedelta(seconds=self.ttl_seconds)

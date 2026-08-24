"""Human session lifetime settings."""

from __future__ import annotations

from datetime import timedelta
from typing import Self

from pydantic import Field, model_validator

from .base import SettingsModel


class SessionSettings(SettingsModel):
    """Validated idle and absolute human session lifetimes."""

    idle_ttl_seconds: int = Field(default=86_400, ge=60, le=2_592_000)
    absolute_ttl_seconds: int = Field(default=2_592_000, ge=60, le=31_536_000)

    @model_validator(mode="after")
    def validate_lifetime_order(self) -> Self:
        """Keep the idle lifetime within the absolute lifetime."""
        if self.idle_ttl_seconds > self.absolute_ttl_seconds:
            raise ValueError("SessionModel idle TTL cannot exceed absolute TTL")
        return self

    @property
    def idle_ttl(self) -> timedelta:
        """Return the idle lifetime as timedelta."""
        return timedelta(seconds=self.idle_ttl_seconds)

    @property
    def absolute_ttl(self) -> timedelta:
        """Return the absolute lifetime as timedelta."""
        return timedelta(seconds=self.absolute_ttl_seconds)

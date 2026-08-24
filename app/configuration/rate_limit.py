"""PostgreSQL authentication rate-limit settings."""

from __future__ import annotations

from datetime import timedelta

from pydantic import Field

from .base import SettingsModel


class RateLimitSettings(SettingsModel):
    """Independent bounded attempt windows and temporary locks for token grants."""

    password_attempts: int = Field(default=10, ge=2, le=100)
    password_window_seconds: int = Field(default=300, ge=10, le=86_400)
    password_lock_seconds: int = Field(default=900, ge=10, le=86_400)
    service_credential_attempts: int = Field(default=20, ge=2, le=100)
    service_credential_window_seconds: int = Field(default=300, ge=10, le=86_400)
    service_credential_lock_seconds: int = Field(default=900, ge=10, le=86_400)

    @property
    def password_window(self) -> timedelta:
        """Return the password-attempt window."""
        return timedelta(seconds=self.password_window_seconds)

    @property
    def password_lock(self) -> timedelta:
        """Return the password temporary lock duration."""
        return timedelta(seconds=self.password_lock_seconds)

    @property
    def service_credential_window(self) -> timedelta:
        """Return the service-credential attempt window."""
        return timedelta(seconds=self.service_credential_window_seconds)

    @property
    def service_credential_lock(self) -> timedelta:
        """Return the service-credential temporary lock duration."""
        return timedelta(seconds=self.service_credential_lock_seconds)

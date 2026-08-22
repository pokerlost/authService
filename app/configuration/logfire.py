"""Logfire delivery and console settings."""

from __future__ import annotations

from typing import Self

from pydantic import Field, SecretStr, model_validator

from .base import SettingsModel


class LogfireSettings(SettingsModel):
    """Single observability backend configuration."""

    send_to_logfire: bool = Field(
        default=False,
        description="Send telemetry to the configured Logfire project.",
    )
    console_enabled: bool = Field(
        default=True,
        description="Render Logfire telemetry to the process console.",
    )
    token: SecretStr | None = Field(
        default=None,
        description="Logfire project write token required for remote delivery.",
        repr=False,
    )

    @model_validator(mode="after")
    def validate_remote_delivery(self) -> Self:
        """Require an explicit secret whenever remote delivery is enabled."""
        if self.send_to_logfire and self.token is None:
            raise ValueError("Logfire token is required when remote delivery is enabled")
        return self

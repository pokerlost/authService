"""Application identity and deployment settings."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from domain.enums import Environment

from .base import SettingsModel


class ApplicationSettings(SettingsModel):
    """Stable service identity and deployment environment."""

    service_name: Literal["authService"] = Field(
        default="authService",
        description="Canonical human-facing service name.",
    )
    version: str = Field(
        default="0.1.0",
        pattern=r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$",
        description="Service contract version exposed through OpenAPI and telemetry.",
    )
    environment: Environment = Field(
        default=Environment.LOCAL,
        description="Current deployment environment.",
    )

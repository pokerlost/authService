"""Validated process settings loaded only when an application is constructed."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    """Values for enabled process resources, with safe error rendering."""

    model_config = SettingsConfigDict(
        env_prefix="AUTHSERVICE_",
        extra="ignore",
        validate_default=True,
        validate_by_name=True,
        hide_input_in_errors=True,
    )

    logLevel: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    databaseUrl: SecretStr = Field(
        default=SecretStr(""), validation_alias="DATABASE_URL", repr=False
    )

    @field_validator("databaseUrl")
    @classmethod
    def validateDatabaseUrl(cls, value: SecretStr) -> SecretStr:
        """Require the async PostgreSQL driver for enabled persistence."""
        if not value.get_secret_value().startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg")
        return value

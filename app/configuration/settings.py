"""Global immutable service settings."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.enums import Environment

from .application import ApplicationSettings
from .database import DatabaseSettings
from .http import HTTPSettings
from .jwt import JWTSettings
from .logfire import LogfireSettings
from .maintenance import MaintenanceSettings
from .oauth2 import OAuth2Settings
from .openapi_registry import OpenAPIRegistrySettings
from .password import PasswordSettings
from .rate_limit import RateLimitSettings
from .refresh_token import RefreshTokenSettings
from .service_auth import ServiceAuthSettings
from .session import SessionSettings


class Settings(BaseSettings):
    """Validated root configuration loaded from environment and a local environment file."""

    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
        validate_default=True,
    )

    application: ApplicationSettings = Field(default_factory=ApplicationSettings)
    database: DatabaseSettings
    http: HTTPSettings = Field(default_factory=HTTPSettings)
    logfire: LogfireSettings = Field(default_factory=LogfireSettings)
    password: PasswordSettings = Field(default_factory=PasswordSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    session: SessionSettings = Field(default_factory=SessionSettings)
    refresh_token: RefreshTokenSettings
    service_auth: ServiceAuthSettings
    openapi_registry: OpenAPIRegistrySettings = Field(default_factory=OpenAPIRegistrySettings)
    oauth2: OAuth2Settings = Field(default_factory=OAuth2Settings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    maintenance: MaintenanceSettings = Field(default_factory=MaintenanceSettings)

    @model_validator(mode="after")
    def validate_production_observability(self) -> Self:
        """Fail fast when production telemetry delivery is disabled."""
        if self.application.environment is Environment.PRODUCTION and not (
            self.logfire.enabled and self.logfire.send_to_logfire
        ):
            raise ValueError("Production requires remote Logfire delivery")
        return self

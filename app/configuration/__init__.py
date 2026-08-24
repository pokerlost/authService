"""Typed service configuration facade."""

from __future__ import annotations

from .jwt import JWTSettings
from .maintenance import MaintenanceSettings
from .oauth2 import OAuth2Settings
from .openapi_registry import OpenAPIRegistrySettings
from .rate_limit import RateLimitSettings
from .refresh_token import RefreshTokenSettings
from .service_auth import ServiceAuthSettings
from .session import SessionSettings
from .settings import Settings

__all__ = (
    "JWTSettings",
    "MaintenanceSettings",
    "OAuth2Settings",
    "OpenAPIRegistrySettings",
    "RateLimitSettings",
    "RefreshTokenSettings",
    "ServiceAuthSettings",
    "SessionSettings",
    "Settings",
)

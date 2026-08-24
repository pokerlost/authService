"""Access JWT signing and JWKS configuration."""

from __future__ import annotations

from datetime import timedelta

from pydantic import Field

from .base import SettingsModel


class JWTSettings(SettingsModel):
    """Configured access-token signing and publication metadata."""

    issuer: str = Field(
        default="authService",
        min_length=1,
        max_length=255,
        description="Stable issuer claim for emitted access tokens.",
    )
    human_audience: str = Field(
        default="authService",
        min_length=1,
        max_length=255,
        description="Audience claim for human access tokens.",
    )
    access_token_ttl_seconds: int = Field(
        default=600,
        description="Human access-token TTL in seconds.",
        ge=60,
        le=86_400,
    )
    clock_skew_seconds: float = Field(
        default=30.0,
        description="JWT verification leeway in seconds.",
        ge=0.0,
        le=300.0,
    )
    active_kid: str = Field(
        default="key-20260822-a",
        min_length=4,
        max_length=64,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{3,63}$",
        description="Stable key identifier for the active signing private key.",
    )
    active_private_key_path: str = Field(
        default="/run/secrets/pokerlost/auth/active-private.pem",
        min_length=1,
        description="Filesystem path to the active RSA private key.",
    )
    retained_public_key_directory: str = Field(
        default="/run/secrets/pokerlost/auth/public",
        min_length=1,
        description="Filesystem directory with retained RSA public keys for JWKS publication.",
    )
    jwks_cache_ttl_seconds: int = Field(
        default=60,
        description="Cache-Control max-age for /jwks.get responses.",
        ge=1,
        le=600,
    )

    @property
    def access_token_ttl(self) -> timedelta:
        """Return configured TTL as timedelta."""
        return timedelta(seconds=self.access_token_ttl_seconds)

    @property
    def clock_skew(self) -> timedelta:
        """Return configured leeway as timedelta."""
        return timedelta(seconds=self.clock_skew_seconds)

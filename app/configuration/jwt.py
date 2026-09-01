"""JWT signing key settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from .base import SettingsModel


class JWTSettings(SettingsModel):
    """Required mounted private-key path and public key identifier."""

    private_key_path: Path = Field(
        description="Filesystem path to the mounted RSA private key.",
    )
    key_id: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9._-]{1,128}$",
        description="Safe public identifier placed in the JWT kid header.",
    )

"""Argon2id password hashing settings."""

from __future__ import annotations

from pydantic import Field

from .base import SettingsModel


class PasswordSettings(SettingsModel):
    """Validated non-secret Argon2id cost parameters."""

    time_cost: int = Field(default=3, ge=1, le=10)
    memory_cost_kib: int = Field(default=65_536, ge=19_456, le=1_048_576)
    parallelism: int = Field(default=4, ge=1, le=16)
    hash_length: int = Field(default=32, ge=16, le=64)
    salt_length: int = Field(default=16, ge=16, le=64)

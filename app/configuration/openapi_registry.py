"""OpenAPI authorization registry resource limits."""

from __future__ import annotations

from pydantic import Field

from .base import SettingsModel


class OpenAPIRegistrySettings(SettingsModel):
    """Bound potentially hostile submitted OpenAPI JSON documents."""

    max_document_bytes: int = Field(default=1_048_576, ge=16_384, le=16_777_216)
    max_operations: int = Field(default=1_000, ge=1, le=10_000)
    max_nesting_depth: int = Field(default=64, ge=8, le=128)

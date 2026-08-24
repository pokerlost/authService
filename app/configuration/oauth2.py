"""OAuth2 request and JWT scope limits."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from .base import SettingsModel


class OAuth2Settings(SettingsModel):
    """Bound requested scopes, serialized claims, and emitted access tokens."""

    max_requested_scopes: int = Field(default=128, ge=1, le=1_000)
    max_scope_token_length: int = Field(default=255, ge=16, le=255)
    max_total_scope_claim_bytes: int = Field(default=16_384, ge=256, le=65_536)
    max_access_token_bytes: int = Field(default=24_576, ge=2_048, le=131_072)

    @model_validator(mode="after")
    def validate_token_capacity(self) -> Self:
        """Reserve bounded JWT encoding overhead above the configured scope claim ceiling."""
        encoded_scope_ceiling = (4 * self.max_total_scope_claim_bytes + 2) // 3
        if self.max_access_token_bytes < encoded_scope_ceiling + 2_048:
            raise ValueError("Access-token byte limit is too small for the scope claim limit")
        return self

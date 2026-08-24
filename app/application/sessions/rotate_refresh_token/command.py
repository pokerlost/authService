"""Refresh-token rotation command."""

from __future__ import annotations

from pydantic import Field, SecretStr

from domain.value_model import ValueModel


class RotateRefreshTokenCommand(ValueModel):
    """Opaque refresh credential supplied to the application core."""

    refresh_token: SecretStr = Field(repr=False)
    requested_scope: str | None = None

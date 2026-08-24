"""One-time AUTO service credential provisioning result."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field, SecretStr

from domain.value_model import ValueModel


class CreatedServiceCredential(ValueModel):
    """Public locator, one-time secret, and finite expiration for an operator."""

    client_id: str
    client_secret: SecretStr = Field(repr=False)
    expires_at: datetime

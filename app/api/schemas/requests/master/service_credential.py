"""Master service credential revocation request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel


class ServiceCredentialRequest(APIModel):
    """Public random service credential identifier selected for revocation."""

    client_id: str = Field(min_length=16, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")

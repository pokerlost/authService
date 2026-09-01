"""Bootstrap-service-client application result."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field, SecretStr

from application import Result


class BootstrapServiceClientResult(Result):
    """One-time confidential client identifier and generated raw secret."""

    client_id: UUID
    client_secret: SecretStr = Field(repr=False)

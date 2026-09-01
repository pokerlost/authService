"""OAuth2 client aggregate."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import AwareDatetime, model_validator
from pydantic_core import PydanticCustomError

from domain.enums import OAuthClientStatus, OAuthClientType
from domain.value_model import ValueModel


class OAuthClient(ValueModel):
    """Public or confidential OAuth2 client with an exact principal binding."""

    client_id: UUID
    client_type: OAuthClientType
    status: OAuthClientStatus
    bound_principal_id: UUID | None
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @model_validator(mode="after")
    def validate_invariants(self) -> Self:
        """Enforce client binding and timestamp invariants."""
        if self.client_type is OAuthClientType.PUBLIC and self.bound_principal_id is not None:
            raise PydanticCustomError(
                "invalid_oauth_client_binding",
                "Public OAuth2 client cannot have a principal binding",
            )
        if self.client_type is OAuthClientType.CONFIDENTIAL and self.bound_principal_id is None:
            raise PydanticCustomError(
                "invalid_oauth_client_binding",
                "Confidential OAuth2 client requires a principal binding",
            )
        if self.updated_at < self.created_at:
            raise PydanticCustomError(
                "invalid_oauth_client_timestamps",
                "OAuth2 client update time cannot precede creation time",
            )
        return self

    @classmethod
    def create_confidential(
        cls,
        *,
        client_id: UUID,
        bound_principal_id: UUID,
        now: datetime,
    ) -> Self:
        """Create an active confidential client for one exact principal."""
        return cls(
            client_id=client_id,
            client_type=OAuthClientType.CONFIDENTIAL,
            status=OAuthClientStatus.ACTIVE,
            bound_principal_id=bound_principal_id,
            created_at=now,
            updated_at=now,
        )

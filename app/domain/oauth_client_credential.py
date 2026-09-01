"""OAuth2 client secret credential value."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, model_validator
from pydantic_core import PydanticCustomError

from domain.enums import OAuthClientCredentialStatus
from domain.value_model import ValueModel

type OAuthClientSecretDigest = Annotated[
    bytes,
    Field(strict=True, min_length=32, max_length=32),
]


class OAuthClientCredential(ValueModel):
    """Digest-only confidential-client credential with explicit lifecycle state."""

    credential_id: UUID
    client_id: UUID
    secret_digest: OAuthClientSecretDigest = Field(repr=False)
    status: OAuthClientCredentialStatus
    created_at: AwareDatetime
    updated_at: AwareDatetime
    expires_at: AwareDatetime | None
    revoked_at: AwareDatetime | None

    @model_validator(mode="after")
    def validate_invariants(self) -> Self:
        """Enforce digest lifecycle and timestamp consistency."""
        if self.updated_at < self.created_at:
            raise PydanticCustomError(
                "invalid_oauth_client_credential_timestamps",
                "Credential update time cannot precede creation time",
            )
        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise PydanticCustomError(
                "invalid_oauth_client_credential_expiry",
                "Credential expiry must follow creation time",
            )
        if self.status is OAuthClientCredentialStatus.REVOKED:
            if self.revoked_at is None:
                raise PydanticCustomError(
                    "invalid_oauth_client_credential_state",
                    "Revoked credential requires a revocation time",
                )
            if self.revoked_at < self.created_at:
                raise PydanticCustomError(
                    "invalid_oauth_client_credential_timestamps",
                    "Credential revocation time cannot precede creation time",
                )
            return self
        if self.revoked_at is not None:
            raise PydanticCustomError(
                "invalid_oauth_client_credential_state",
                "Accepted credential state cannot have a revocation time",
            )
        return self

    @classmethod
    def create_active(
        cls,
        *,
        credential_id: UUID,
        client_id: UUID,
        secret_digest: bytes,
        now: datetime,
        expires_at: datetime | None = None,
    ) -> Self:
        """Create one active digest-only credential."""
        return cls(
            credential_id=credential_id,
            client_id=client_id,
            secret_digest=secret_digest,
            status=OAuthClientCredentialStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            expires_at=expires_at,
            revoked_at=None,
        )

    def accepts_at(self, at: datetime) -> bool:
        """Return whether this credential may authenticate at an aware instant."""
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("Credential acceptance time must be timezone-aware")
        if self.status not in (
            OAuthClientCredentialStatus.ACTIVE,
            OAuthClientCredentialStatus.RETIRING,
        ):
            return False
        if at < self.created_at:
            return False
        return self.expires_at is None or at < self.expires_at

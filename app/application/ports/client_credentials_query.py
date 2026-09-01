"""Client-credentials authorization query port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self
from uuid import UUID

from pydantic import model_validator
from pydantic_core import PydanticCustomError

from domain.enums import (
    OAuthClientStatus,
    OAuthClientType,
    OAuthGrantType,
    PrincipalStatus,
    PrincipalType,
    RoleCode,
)
from domain.oauth_client_credential import OAuthClientCredential
from domain.resource_indicator import ResourceIndicator
from domain.scope_name import ScopeName
from domain.value_model import ValueModel


class ClientCredentialsAuthorizationContext(ValueModel):
    """Immutable authorization facts required for service-token issuance."""

    client_id: UUID
    client_type: OAuthClientType
    client_status: OAuthClientStatus
    bound_principal_id: UUID | None
    principal_id: UUID | None
    principal_type: PrincipalType | None
    principal_role: RoleCode | None
    principal_status: PrincipalStatus | None
    service_slug: str | None
    credentials: tuple[OAuthClientCredential, ...]
    grant_types: frozenset[OAuthGrantType]
    service_scopes: frozenset[ScopeName]
    client_scopes: frozenset[ScopeName]
    service_audiences: frozenset[ResourceIndicator]
    client_audiences: frozenset[ResourceIndicator]

    @model_validator(mode="after")
    def validate_credential_ownership(self) -> Self:
        """Reject a query result containing another client's credential."""
        if any(credential.client_id != self.client_id for credential in self.credentials):
            raise PydanticCustomError(
                "invalid_client_credentials_context",
                "Credential does not belong to the queried OAuth2 client",
            )
        return self


class ClientCredentialsQuery(ABC):
    """Read exact persisted authorization facts for one OAuth2 client."""

    @abstractmethod
    async def get_authorization_context(
        self,
        client_id: UUID,
    ) -> ClientCredentialsAuthorizationContext | None:
        """Return the exact client context without ORM entities."""
        raise NotImplementedError

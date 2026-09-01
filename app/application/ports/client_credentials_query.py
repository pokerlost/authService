"""Client-credentials authorization query port."""

from __future__ import annotations

from typing import Protocol, Self
from uuid import UUID

from pydantic import model_validator
from pydantic_core import PydanticCustomError
from pypokerlost.contracts.authorization import (
    AuthorizationRole,
    PrincipalStatus,
    PrincipalType,
)
from pypokerlost.types import OAuthScope

from domain.enums import (
    OAuthClientStatus,
    OAuthClientType,
    OAuthGrantType,
)
from domain.oauth_client_credential import OAuthClientCredential
from domain.resource_indicator import ResourceIndicator
from domain.value_model import ValueModel


class ClientCredentialsAuthorizationContext(ValueModel):
    """Immutable authorization facts required for service-token issuance."""

    client_id: UUID
    client_type: OAuthClientType
    client_status: OAuthClientStatus
    bound_principal_id: UUID | None
    principal_id: UUID | None
    principal_type: PrincipalType | None
    principal_role: AuthorizationRole | None
    principal_status: PrincipalStatus | None
    service_slug: str | None
    credentials: tuple[OAuthClientCredential, ...]
    grant_types: frozenset[OAuthGrantType]
    service_scopes: frozenset[OAuthScope]
    client_scopes: frozenset[OAuthScope]
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


class ClientCredentialsQuery(Protocol):
    """Read exact persisted authorization facts for one OAuth2 client."""

    async def get_authorization_context(
        self,
        client_id: UUID,
    ) -> ClientCredentialsAuthorizationContext | None:
        """Return the exact client context without ORM entities."""
        ...

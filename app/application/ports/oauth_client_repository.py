"""OAuth2 client bootstrap repository port."""

from __future__ import annotations

from collections.abc import Collection
from datetime import datetime
from typing import Protocol
from uuid import UUID

from pypokerlost.types import PokerlostAudience

from domain.enums import OAuthGrantType
from domain.oauth_client import OAuthClient
from domain.oauth_client_credential import OAuthClientCredential
from domain.scope_definition import ScopeDefinition


class OAuthClientRepository(Protocol):
    """Stage one OAuth2 client bundle in the caller-owned transaction."""

    async def add(self, client: OAuthClient) -> None:
        """Stage one new OAuth2 client."""
        ...

    async def get_by_client_id(self, client_id: UUID) -> OAuthClient | None:
        """Return the client with the exact identifier when it exists."""
        ...

    async def add_grant_type(
        self,
        client_id: UUID,
        grant_type: OAuthGrantType,
        *,
        created_at: datetime,
    ) -> None:
        """Stage one explicit grant-type permission."""
        ...

    async def add_credential(self, credential: OAuthClientCredential) -> None:
        """Stage one digest-only OAuth2 client credential."""
        ...

    async def add_principal_scope_grants(
        self,
        principal_id: UUID,
        scopes: Collection[ScopeDefinition],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact direct scope grants for one principal."""
        ...

    async def add_client_scope_grants(
        self,
        client_id: UUID,
        scopes: Collection[ScopeDefinition],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact direct scope grants for one OAuth2 client."""
        ...

    async def add_principal_audience_grants(
        self,
        principal_id: UUID,
        audiences: Collection[PokerlostAudience],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact audience grants for one principal."""
        ...

    async def add_client_audience_grants(
        self,
        client_id: UUID,
        audiences: Collection[PokerlostAudience],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact audience grants for one OAuth2 client."""
        ...

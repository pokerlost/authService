"""OAuth2 client bootstrap repository port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from domain.enums import OAuthGrantType
from domain.oauth_client import OAuthClient
from domain.oauth_client_credential import OAuthClientCredential
from domain.oauth_scope import OAuthScope
from domain.resource_indicator import ResourceIndicator


class OAuthClientRepository(ABC):
    """Stage one OAuth2 client bundle in the caller-owned transaction."""

    @abstractmethod
    async def add(self, client: OAuthClient) -> None:
        """Stage one new OAuth2 client."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_client_id(self, client_id: UUID) -> OAuthClient | None:
        """Return the client with the exact identifier when it exists."""
        raise NotImplementedError

    @abstractmethod
    async def add_grant_type(
        self,
        client_id: UUID,
        grant_type: OAuthGrantType,
        *,
        created_at: datetime,
    ) -> None:
        """Stage one explicit grant-type permission."""
        raise NotImplementedError

    @abstractmethod
    async def add_credential(self, credential: OAuthClientCredential) -> None:
        """Stage one digest-only OAuth2 client credential."""
        raise NotImplementedError

    @abstractmethod
    async def add_service_scope_grants(
        self,
        principal_id: UUID,
        scopes: Collection[OAuthScope],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact direct scope grants for one service principal."""
        raise NotImplementedError

    @abstractmethod
    async def add_client_scope_grants(
        self,
        client_id: UUID,
        scopes: Collection[OAuthScope],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact direct scope grants for one OAuth2 client."""
        raise NotImplementedError

    @abstractmethod
    async def add_service_audience_grants(
        self,
        principal_id: UUID,
        audiences: Collection[ResourceIndicator],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact audience grants for one service principal."""
        raise NotImplementedError

    @abstractmethod
    async def add_client_audience_grants(
        self,
        client_id: UUID,
        audiences: Collection[ResourceIndicator],
        *,
        created_at: datetime,
    ) -> None:
        """Stage exact audience grants for one OAuth2 client."""
        raise NotImplementedError

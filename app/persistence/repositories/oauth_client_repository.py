"""SQLAlchemy OAuth2 client repository adapter."""

from __future__ import annotations

from collections.abc import Collection
from datetime import datetime
from typing import Never
from uuid import UUID

from pypokerlost.enums import PrincipalType
from pypokerlost.types import PokerlostAudience
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError

from application.errors import IntegrityError as ApplicationIntegrityError
from application.errors import OAuthClientConflictError
from application.ports import OAuthClientRepository
from domain.enums import OAuthClientStatus, OAuthClientType, OAuthGrantType
from domain.oauth_client import OAuthClient
from domain.oauth_client_credential import OAuthClientCredential
from domain.scope_definition import ScopeDefinition
from persistence.database.models import (
    ClientAudienceGrantModel,
    ClientCredentialModel,
    ClientScopeGrantModel,
    OAuthClientGrantTypeModel,
    OAuthClientModel,
    PrincipalAudienceGrantModel,
    PrincipalScopeGrantModel,
)

from .base import SQLAlchemyRepository

_CLIENT_ID_CONSTRAINT = "pk_oauth_clients"


def _constraint_name(exception: SQLAlchemyIntegrityError) -> str | None:
    """Read a PostgreSQL constraint name without a private driver dependency."""
    current: BaseException | None = exception.orig
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        name = getattr(current, "constraint_name", None)
        if isinstance(name, str):
            return name
        current = current.__cause__ or current.__context__
    return None


def _raise_integrity_error(exception: SQLAlchemyIntegrityError) -> Never:
    """Translate a client identifier race and sanitize every other violation."""
    if _constraint_name(exception) == _CLIENT_ID_CONSTRAINT:
        raise OAuthClientConflictError from exception
    raise ApplicationIntegrityError from exception


class SQLAlchemyOAuthClientRepository(SQLAlchemyRepository, OAuthClientRepository):
    """Stage OAuth2 client and bootstrap grant writes in the caller transaction."""

    async def add(self, client: OAuthClient) -> None:
        """Add and flush one OAuth2 client aggregate."""
        model = OAuthClientModel(
            id=client.client_id,
            client_type=client.client_type.value,
            status=client.status.value,
            bound_principal_id=client.bound_principal_id,
            bound_principal_type=(
                PrincipalType.SERVICE.value
                if client.client_type is OAuthClientType.CONFIDENTIAL
                else None
            ),
            created_at=client.created_at,
            updated_at=client.updated_at,
        )
        self._session.add(model)
        await self._flush((model,))

    async def get_by_client_id(self, client_id: UUID) -> OAuthClient | None:
        """Return the OAuth2 client with the exact identifier."""
        result = await self._read_scalar(
            select(OAuthClientModel).where(OAuthClientModel.id == client_id),
        )
        model = result.one_or_none()
        if model is None:
            return None
        return OAuthClient(
            client_id=model.id,
            client_type=OAuthClientType(model.client_type),
            status=OAuthClientStatus(model.status),
            bound_principal_id=model.bound_principal_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def add_grant_type(
        self,
        client_id: UUID,
        grant_type: OAuthGrantType,
        *,
        created_at: datetime,
    ) -> None:
        """Add and flush one explicit client grant-type permission."""
        model = OAuthClientGrantTypeModel(
            client_id=client_id,
            grant_type=grant_type.value,
            created_at=created_at,
        )
        self._session.add(model)
        await self._flush((model,))

    async def add_credential(self, credential: OAuthClientCredential) -> None:
        """Add and flush one digest-only OAuth2 client credential."""
        model = ClientCredentialModel(
            id=credential.credential_id,
            client_id=credential.client_id,
            secret_digest=credential.secret_digest,
            status=credential.status.value,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
            expires_at=credential.expires_at,
            revoked_at=credential.revoked_at,
        )
        self._session.add(model)
        await self._flush((model,))

    async def add_principal_scope_grants(
        self,
        principal_id: UUID,
        scopes: Collection[ScopeDefinition],
        *,
        created_at: datetime,
    ) -> None:
        """Add and flush exact direct principal scope grants."""
        models = tuple(
            PrincipalScopeGrantModel(
                principal_id=principal_id,
                scope_id=scope.scope_id,
                created_at=created_at,
            )
            for scope in scopes
        )
        await self._add_all(models)

    async def add_client_scope_grants(
        self,
        client_id: UUID,
        scopes: Collection[ScopeDefinition],
        *,
        created_at: datetime,
    ) -> None:
        """Add and flush exact direct OAuth2 client scope grants."""
        models = tuple(
            ClientScopeGrantModel(
                client_id=client_id,
                scope_id=scope.scope_id,
                created_at=created_at,
            )
            for scope in scopes
        )
        await self._add_all(models)

    async def add_principal_audience_grants(
        self,
        principal_id: UUID,
        audiences: Collection[PokerlostAudience],
        *,
        created_at: datetime,
    ) -> None:
        """Add and flush exact direct principal audience grants."""
        models = tuple(
            PrincipalAudienceGrantModel(
                principal_id=principal_id,
                audience=str(audience),
                created_at=created_at,
            )
            for audience in audiences
        )
        await self._add_all(models)

    async def add_client_audience_grants(
        self,
        client_id: UUID,
        audiences: Collection[PokerlostAudience],
        *,
        created_at: datetime,
    ) -> None:
        """Add and flush exact direct OAuth2 client audience grants."""
        models = tuple(
            ClientAudienceGrantModel(
                client_id=client_id,
                audience=str(audience),
                created_at=created_at,
            )
            for audience in audiences
        )
        await self._add_all(models)

    async def _add_all(
        self,
        models: tuple[
            PrincipalScopeGrantModel
            | ClientScopeGrantModel
            | PrincipalAudienceGrantModel
            | ClientAudienceGrantModel,
            ...,
        ],
    ) -> None:
        if not models:
            return
        self._session.add_all(models)
        await self._flush(models)

    async def _flush(self, models: tuple[object, ...]) -> None:
        try:
            await self._session.flush(models)
        except SQLAlchemyIntegrityError as exception:
            _raise_integrity_error(exception)

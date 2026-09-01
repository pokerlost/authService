"""Transactional service-principal and confidential-client bootstrap orchestration."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from application import Handler
from application.errors import OAuthClientConflictError, PrincipalConflictError
from application.ports import (
    AuthorizationPrincipalRepository,
    OAuthClientRepository,
    OAuthClientSecretProcessor,
    RoleScopeQuery,
)
from domain.authorization_principal import AuthorizationPrincipal
from domain.enums import OAuthGrantType
from domain.oauth_client import OAuthClient
from domain.oauth_client_credential import OAuthClientCredential

from .command import BootstrapServiceClientCommand
from .result import BootstrapServiceClientResult


class BootstrapServiceClientHandler(
    Handler[BootstrapServiceClientCommand, BootstrapServiceClientResult],
):
    """Create one complete service-client authorization bundle without committing it."""

    __slots__ = (
        "_client_repository",
        "_principal_repository",
        "_role_scope_query",
        "_secret_processor",
    )

    def __init__(
        self,
        principal_repository: AuthorizationPrincipalRepository,
        client_repository: OAuthClientRepository,
        role_scope_query: RoleScopeQuery,
        secret_processor: OAuthClientSecretProcessor,
    ) -> None:
        """Store caller-transaction adapters and the focused secret processor."""
        self._principal_repository = principal_repository
        self._client_repository = client_repository
        self._role_scope_query = role_scope_query
        self._secret_processor = secret_processor

    async def execute(
        self,
        input_: BootstrapServiceClientCommand,
        /,
    ) -> BootstrapServiceClientResult:
        """Stage one exact bundle and return its raw secret only to the caller."""
        scopes = await self._role_scope_query.get_scopes_by_exact_names(input_.scopes)
        existing_principal = await self._principal_repository.get_service_by_service_slug(
            input_.service_slug,
        )
        if existing_principal is not None:
            raise PrincipalConflictError

        client_id = input_.client_id if input_.client_id is not None else uuid4()
        if await self._client_repository.get_by_client_id(client_id) is not None:
            raise OAuthClientConflictError

        now = datetime.now(UTC)
        principal_id = _new_distinct_principal_id(client_id)
        principal = AuthorizationPrincipal.create_service(
            principal_id=principal_id,
            service_slug=input_.service_slug,
            now=now,
        )
        client = OAuthClient.create_confidential(
            client_id=client_id,
            bound_principal_id=principal_id,
            now=now,
        )
        generated_secret = self._secret_processor.generate()
        credential = OAuthClientCredential.create_active(
            credential_id=uuid4(),
            client_id=client_id,
            secret_digest=generated_secret.digest,
            now=now,
        )

        await self._principal_repository.add(principal)
        await self._client_repository.add(client)
        await self._client_repository.add_grant_type(
            client_id,
            OAuthGrantType.CLIENT_CREDENTIALS,
            created_at=now,
        )
        await self._client_repository.add_service_scope_grants(
            principal_id,
            scopes,
            created_at=now,
        )
        await self._client_repository.add_client_scope_grants(
            client_id,
            scopes,
            created_at=now,
        )
        await self._client_repository.add_service_audience_grants(
            principal_id,
            input_.resources,
            created_at=now,
        )
        await self._client_repository.add_client_audience_grants(
            client_id,
            input_.resources,
            created_at=now,
        )
        await self._client_repository.add_credential(credential)
        return BootstrapServiceClientResult(
            client_id=client_id,
            client_secret=generated_secret.secret,
        )


def _new_distinct_principal_id(client_id: UUID) -> UUID:
    """Generate a principal identifier distinct from its OAuth2 client identifier."""
    principal_id = uuid4()
    while principal_id == client_id:
        principal_id = uuid4()
    return principal_id

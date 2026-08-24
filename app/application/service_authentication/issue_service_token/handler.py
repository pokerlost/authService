"""Audience-isolated AUTO token issuance orchestration."""

from __future__ import annotations

from application.errors import InvalidOAuthScope, InvalidServiceCredentials
from application.security import (
    MachineAccessTokenIssuer,
    OAuthScopeParser,
    ServiceCredentialProtector,
)
from application.time import UtcClock, utc_now
from domain.enums import PrincipalStatus, Role, ServiceCredentialStatus
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyPrincipalRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServiceCredentialRepository,
    SQLAlchemyServicePrincipalRepository,
)

from .command import IssueServiceTokenCommand
from .result import IssueServiceTokenResult


class IssueServiceTokenHandler:
    """Authenticate a service credential and issue one audience-bound AUTO JWT."""

    __slots__ = (
        "_clock",
        "_grant_repository",
        "_issuer",
        "_principal_repository",
        "_protector",
        "_scope_parser",
        "_scope_query",
        "_service_credential_repository",
        "_service_principal_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        service_principal_repository: SQLAlchemyServicePrincipalRepository,
        service_credential_repository: SQLAlchemyServiceCredentialRepository,
        grant_repository: SQLAlchemyServiceAudienceGrantRepository,
        protector: ServiceCredentialProtector,
        issuer: MachineAccessTokenIssuer,
        scope_query: SQLAlchemyScopeQuery,
        scope_parser: OAuthScopeParser,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._service_principal_repository = service_principal_repository
        self._service_credential_repository = service_credential_repository
        self._grant_repository = grant_repository
        self._protector = protector
        self._issuer = issuer
        self._scope_query = scope_query
        self._scope_parser = scope_parser
        self._clock = clock

    async def execute(self, command: IssueServiceTokenCommand) -> IssueServiceTokenResult:
        """Return one generic failure for every unusable identity, credential, or grant."""
        credential = await self._service_credential_repository.get_by_client_id(command.client_id)
        verified = self._protector.verify(
            client_id=command.client_id,
            client_secret=command.client_secret,
            expected_digest=(credential.secret_digest if credential is not None else None),
        )
        now = self._clock()
        if (
            credential is None
            or not verified
            or credential.status is not ServiceCredentialStatus.ACTIVE
            or now >= credential.expires_at
        ):
            raise InvalidServiceCredentials

        service_principal = await self._service_principal_repository.get_by_principal_id(
            credential.service_principal_id,
        )
        if service_principal is None:
            raise InvalidServiceCredentials
        principal = await self._principal_repository.get_by_id(service_principal.principal_id)
        if (
            principal is None
            or principal.status is not PrincipalStatus.ACTIVE
            or principal.role is not Role.AUTO
        ):
            raise InvalidServiceCredentials
        if not await self._grant_repository.has_grant(
            service_principal_id=service_principal.principal_id,
            audience=command.audience,
        ):
            raise InvalidServiceCredentials

        active_grants = await self._scope_query.list_active_for_service(
            service_principal_id=service_principal.principal_id,
            audience=command.audience,
        )
        allowed_scopes = frozenset(
            grant.api_operation_id
            for grant in active_grants
            if grant.owner_service_id.lower() == command.audience
        )
        try:
            requested_scopes = self._scope_parser.parse_requested(command.requested_scope)
        except ValueError:
            raise InvalidOAuthScope from None
        if command.requested_scope is None or not command.requested_scope.strip():
            scopes = allowed_scopes
        elif not requested_scopes.issubset(allowed_scopes):
            raise InvalidOAuthScope
        else:
            scopes = requested_scopes

        return IssueServiceTokenResult(
            access_token=self._issuer.issue_machine_access_token(
                principal_id=principal.id,
                service=service_principal.service_slug,
                audience=command.audience,
                scopes=scopes,
            ),
            scopes=scopes,
            principal_id=principal.id,
        )

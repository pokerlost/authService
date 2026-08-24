"""AUTO service credential provisioning orchestration."""

from __future__ import annotations

from datetime import timedelta

from application.errors import IntegrityError, ServicePrincipalNotFound
from application.security import ServiceCredentialProtector
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, Role
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyServiceCredentialRepository,
    SQLAlchemyServicePrincipalRepository,
)

from .command import CreateServiceCredentialCommand
from .result import CreatedServiceCredential


class CreateServiceCredentialHandler:
    """Create one finite credential and return its raw secret exactly once."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_credential_ttl",
        "_principal_repository",
        "_protector",
        "_service_credential_repository",
        "_service_principal_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        service_principal_repository: SQLAlchemyServicePrincipalRepository,
        service_credential_repository: SQLAlchemyServiceCredentialRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        protector: ServiceCredentialProtector,
        credential_ttl: timedelta,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._service_principal_repository = service_principal_repository
        self._service_credential_repository = service_credential_repository
        self._audit_repository = audit_repository
        self._protector = protector
        self._credential_ttl = credential_ttl
        self._clock = clock

    async def execute(self, command: CreateServiceCredentialCommand) -> CreatedServiceCredential:
        """Persist only HMAC material for an existing AUTO service principal."""
        service_principal = await self._service_principal_repository.get_by_service_slug(
            command.service_slug,
        )
        if service_principal is None:
            raise ServicePrincipalNotFound
        principal = await self._principal_repository.get_by_id(service_principal.principal_id)
        if principal is None or principal.role is not Role.AUTO:
            raise IntegrityError

        issued = self._protector.generate()
        expires_at = self._clock() + self._credential_ttl
        credential = await self._service_credential_repository.create(
            service_principal_id=service_principal.principal_id,
            client_id=issued.client_id,
            secret_digest=issued.secret_digest,
            expires_at=expires_at,
        )
        if credential is None:
            raise IntegrityError
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.SERVICE_CREDENTIAL_CREATED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="service_credential",
            target_id=str(credential.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"servicePrincipalId": str(service_principal.principal_id)},
        )
        return CreatedServiceCredential(
            client_id=issued.client_id,
            client_secret=issued.client_secret,
            expires_at=credential.expires_at,
        )

"""AUTO service principal provisioning orchestration."""

from __future__ import annotations

from application.errors import ServicePrincipalAlreadyExists
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, PrincipalStatus, Role
from persistence.database.models import ServicePrincipalModel
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyServicePrincipalRepository,
)

from .command import CreateServicePrincipalCommand


class CreateServicePrincipalHandler:
    """Atomically create one active AUTO principal and service identity."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_principal_repository",
        "_service_principal_repository",
    )

    def __init__(
        self,
        *,
        principal_repository: SQLAlchemyPrincipalRepository,
        service_principal_repository: SQLAlchemyServicePrincipalRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._principal_repository = principal_repository
        self._service_principal_repository = service_principal_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: CreateServicePrincipalCommand) -> ServicePrincipalModel:
        """Create both rows in the caller-owned transaction without orphaning PrincipalModel."""
        principal = await self._principal_repository.create(
            role=Role.AUTO,
            status=PrincipalStatus.ACTIVE,
        )
        service_principal = await self._service_principal_repository.create(
            principal_id=principal.id,
            service_slug=command.service_slug,
        )
        if service_principal is None:
            raise ServicePrincipalAlreadyExists
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.SERVICE_PRINCIPAL_CREATED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="service_principal",
            target_id=str(service_principal.principal_id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"serviceSlug": service_principal.service_slug},
        )
        return service_principal

"""AUTO service audience grant orchestration."""

from __future__ import annotations

from application.errors import ServicePrincipalNotFound
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServicePrincipalRepository,
)

from .command import GrantServiceAudienceCommand


class GrantServiceAudienceHandler:
    """Idempotently permit one service to request one target audience."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_grant_repository",
        "_service_principal_repository",
    )

    def __init__(
        self,
        *,
        service_principal_repository: SQLAlchemyServicePrincipalRepository,
        grant_repository: SQLAlchemyServiceAudienceGrantRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._service_principal_repository = service_principal_repository
        self._grant_repository = grant_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: GrantServiceAudienceCommand) -> None:
        """Create one exact source-to-target grant in the caller transaction."""
        service_principal = await self._service_principal_repository.get_by_service_slug(
            command.service_slug,
        )
        if service_principal is None:
            raise ServicePrincipalNotFound
        created = await self._grant_repository.grant(
            service_principal_id=service_principal.principal_id,
            audience=command.audience,
        )
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.SERVICE_AUDIENCE_GRANTED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="service_audience",
            target_id=f"{service_principal.principal_id}:{command.audience}",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"created": created},
        )

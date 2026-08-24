"""Service scope grant orchestration."""

from __future__ import annotations

from application.errors import ScopeGrantInvalidError, ServicePrincipalNotFound
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServicePrincipalRepository,
    SQLAlchemyServiceScopeGrantRepository,
)

from .command import GrantServiceScopeCommand


class GrantServiceScopeHandler:
    """Require exact source, audience, active ownership, and scope before granting."""

    __slots__ = (
        "_audience_repository",
        "_audit_repository",
        "_clock",
        "_grant_repository",
        "_scope_query",
        "_service_principal_repository",
    )

    def __init__(
        self,
        *,
        service_principal_repository: SQLAlchemyServicePrincipalRepository,
        audience_repository: SQLAlchemyServiceAudienceGrantRepository,
        grant_repository: SQLAlchemyServiceScopeGrantRepository,
        scope_query: SQLAlchemyScopeQuery,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._service_principal_repository = service_principal_repository
        self._audience_repository = audience_repository
        self._grant_repository = grant_repository
        self._scope_query = scope_query
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: GrantServiceScopeCommand) -> None:
        """Create one service scope grant only for its owning target resource."""
        service_principal = await self._service_principal_repository.get_by_service_slug(
            command.service_slug
        )
        if service_principal is None:
            raise ServicePrincipalNotFound
        if not await self._audience_repository.has_grant(
            service_principal_id=service_principal.principal_id,
            audience=command.audience,
        ):
            raise ScopeGrantInvalidError
        active_scope = await self._scope_query.get_active(command.scope)
        if active_scope is None or active_scope.owner_service_id.lower() != command.audience:
            raise ScopeGrantInvalidError
        created = await self._grant_repository.grant(
            service_principal_id=service_principal.principal_id,
            audience=command.audience,
            api_operation_id=command.scope,
        )
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.SERVICE_SCOPE_GRANTED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="service_scope",
            target_id=f"{service_principal.principal_id}:{command.audience}:{command.scope}",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"created": created},
        )

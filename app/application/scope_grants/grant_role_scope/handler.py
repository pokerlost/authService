"""Role scope grant orchestration."""

from __future__ import annotations

from application.errors import ScopeGrantInvalidError
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRoleScopeGrantRepository,
)

from .command import GrantRoleScopeCommand


class GrantRoleScopeHandler:
    """Create one explicit direct human role grant with same-transaction audit."""

    __slots__ = ("_audit_repository", "_clock", "_grant_repository", "_scope_query")

    def __init__(
        self,
        *,
        grant_repository: SQLAlchemyRoleScopeGrantRepository,
        scope_query: SQLAlchemyScopeQuery,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._grant_repository = grant_repository
        self._scope_query = scope_query
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: GrantRoleScopeCommand) -> None:
        """Validate active ownership and idempotently create the grant."""
        if not command.role.is_human:
            raise ScopeGrantInvalidError
        active_scope = await self._scope_query.get_active(command.scope)
        if active_scope is None:
            raise ScopeGrantInvalidError
        created = await self._grant_repository.grant(
            role=command.role,
            api_operation_id=command.scope,
        )
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.ROLE_SCOPE_GRANTED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="role_scope",
            target_id=f"{command.role.value}:{command.scope}",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"created": created},
        )

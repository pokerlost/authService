"""Role scope revocation orchestration."""

from __future__ import annotations

from application.errors import ScopeGrantInvalidError
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRoleScopeGrantRepository,
)

from .command import RevokeRoleScopeCommand


class RevokeRoleScopeHandler:
    """Idempotently remove one human role scope grant and append audit."""

    __slots__ = ("_audit_repository", "_clock", "_grant_repository")

    def __init__(
        self,
        *,
        grant_repository: SQLAlchemyRoleScopeGrantRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._grant_repository = grant_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: RevokeRoleScopeCommand) -> None:
        """Remove a grant without changing already-issued access JWTs."""
        if not command.role.is_human:
            raise ScopeGrantInvalidError
        removed = await self._grant_repository.revoke(
            role=command.role,
            api_operation_id=command.scope,
        )
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.ROLE_SCOPE_REVOKED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="role_scope",
            target_id=f"{command.role.value}:{command.scope}",
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"removed": removed},
        )

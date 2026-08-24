"""AUTO service credential revocation orchestration."""

from __future__ import annotations

from application.errors import ServiceCredentialNotFound
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyServiceCredentialRepository,
)

from .command import RevokeServiceCredentialCommand


class RevokeServiceCredentialHandler:
    """Idempotently block future issuance through one known client ID."""

    __slots__ = ("_audit_repository", "_clock", "_repository")

    def __init__(
        self,
        repository: SQLAlchemyServiceCredentialRepository,
        *,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._repository = repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(self, command: RevokeServiceCredentialCommand) -> None:
        """Persist explicit revocation while preserving already-issued JWT validity."""
        now = self._clock()
        credential = await self._repository.revoke(
            client_id=command.client_id,
            revoked_at=now,
        )
        if credential is None:
            raise ServiceCredentialNotFound
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=now,
            event_type=AuditEventType.SERVICE_CREDENTIAL_REVOKED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="service_credential",
            target_id=str(credential.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"servicePrincipalId": str(credential.service_principal_id)},
        )

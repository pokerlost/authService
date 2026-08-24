"""Bounded security-state cleanup orchestration."""

from __future__ import annotations

from datetime import timedelta

from application.time import UtcClock, utc_now
from persistence.repositories import SQLAlchemySecurityCleanupRepository

from .command import CleanupSecurityStateCommand
from .result import CleanupSummary


class CleanupSecurityStateHandler:
    """Apply independent retention cutoffs without touching permanent authorization state."""

    __slots__ = ("_clock", "_repository")

    def __init__(
        self,
        repository: SQLAlchemySecurityCleanupRepository,
        *,
        clock: UtcClock = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock

    async def execute(self, command: CleanupSecurityStateCommand) -> CleanupSummary:
        """Run one bounded pass over each explicitly retention-eligible table."""
        now = self._clock()
        security_cutoff = now - timedelta(days=command.security_state_retention_days)
        audit_cutoff = now - timedelta(days=command.audit_retention_days)
        refresh_tokens = await self._repository.cleanup_refresh_tokens(
            cutoff=security_cutoff,
            limit=command.batch_size,
            dry_run=command.dry_run,
        )
        sessions = await self._repository.cleanup_sessions(
            cutoff=security_cutoff,
            limit=command.batch_size,
            dry_run=command.dry_run,
        )
        service_credentials = await self._repository.cleanup_service_credentials(
            cutoff=security_cutoff,
            limit=command.batch_size,
            dry_run=command.dry_run,
        )
        rate_limit_rows = await self._repository.cleanup_rate_limits(
            cutoff=security_cutoff,
            now=now,
            limit=command.batch_size,
            dry_run=command.dry_run,
        )
        audit_events = await self._repository.cleanup_audit_events(
            cutoff=audit_cutoff,
            limit=command.batch_size,
            dry_run=command.dry_run,
        )
        return CleanupSummary(
            dry_run=command.dry_run,
            refresh_tokens=refresh_tokens,
            sessions=sessions,
            service_credentials=service_credentials,
            rate_limit_rows=rate_limit_rows,
            audit_events=audit_events,
        )

"""Bounded retention cleanup persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, delete, exists, or_, select

from persistence.database.models import (
    AuditEventModel,
    RefreshTokenModel,
    SecurityRateLimitModel,
    ServiceCredentialModel,
    SessionModel,
)
from persistence.projections import SecurityRateLimitKeyProjection

from .base import SQLAlchemyRepository


class SQLAlchemySecurityCleanupRepository(SQLAlchemyRepository):
    """Delete only bounded retention-eligible security state batches."""

    async def cleanup_refresh_tokens(
        self,
        *,
        cutoff: datetime,
        limit: int,
        dry_run: bool,
    ) -> int:
        """Delete old unreferenced refresh-chain leaves in one bounded batch."""
        child = RefreshTokenModel.__table__.alias("refresh_token_child")
        candidate_ids = await self._candidate_ids(
            select(RefreshTokenModel.id)
            .where(
                RefreshTokenModel.expires_at < cutoff,
                or_(
                    RefreshTokenModel.consumed_at.is_(None),
                    RefreshTokenModel.consumed_at < cutoff,
                ),
                or_(
                    RefreshTokenModel.revoked_at.is_(None),
                    RefreshTokenModel.revoked_at < cutoff,
                ),
                or_(
                    RefreshTokenModel.reuse_detected_at.is_(None),
                    RefreshTokenModel.reuse_detected_at < cutoff,
                ),
                ~exists(
                    select(child.c.id).where(
                        or_(
                            child.c.parent_token_id == RefreshTokenModel.id,
                            child.c.replaced_by_token_id == RefreshTokenModel.id,
                        )
                    )
                ),
            )
            .order_by(RefreshTokenModel.expires_at, RefreshTokenModel.id)
            .limit(limit)
        )
        return await self._delete_ids(
            model=RefreshTokenModel,
            candidate_ids=candidate_ids,
            dry_run=dry_run,
        )

    async def cleanup_sessions(
        self,
        *,
        cutoff: datetime,
        limit: int,
        dry_run: bool,
    ) -> int:
        """Delete old terminal sessions only after their refresh rows are gone."""
        candidate_ids = await self._candidate_ids(
            select(SessionModel.id)
            .where(
                or_(
                    SessionModel.absolute_expires_at < cutoff,
                    SessionModel.revoked_at < cutoff,
                ),
                ~exists(
                    select(RefreshTokenModel.id).where(
                        RefreshTokenModel.session_id == SessionModel.id
                    )
                ),
            )
            .order_by(SessionModel.absolute_expires_at, SessionModel.id)
            .limit(limit)
        )
        return await self._delete_ids(
            model=SessionModel,
            candidate_ids=candidate_ids,
            dry_run=dry_run,
        )

    async def cleanup_service_credentials(
        self,
        *,
        cutoff: datetime,
        limit: int,
        dry_run: bool,
    ) -> int:
        """Delete only credentials expired or revoked before the retention cutoff."""
        candidate_ids = await self._candidate_ids(
            select(ServiceCredentialModel.id)
            .where(
                or_(
                    ServiceCredentialModel.expires_at < cutoff,
                    ServiceCredentialModel.revoked_at < cutoff,
                )
            )
            .order_by(ServiceCredentialModel.expires_at, ServiceCredentialModel.id)
            .limit(limit)
        )
        return await self._delete_ids(
            model=ServiceCredentialModel,
            candidate_ids=candidate_ids,
            dry_run=dry_run,
        )

    async def cleanup_rate_limits(
        self,
        *,
        cutoff: datetime,
        now: datetime,
        limit: int,
        dry_run: bool,
    ) -> int:
        """Delete stale attempt windows whose temporary lock is no longer active."""
        key_rows = await self._read_projection(
            select(
                SecurityRateLimitModel.kind.label("kind"),
                SecurityRateLimitModel.key_fingerprint.label("key_fingerprint"),
            )
            .where(
                SecurityRateLimitModel.updated_at < cutoff,
                or_(
                    SecurityRateLimitModel.locked_until.is_(None),
                    SecurityRateLimitModel.locked_until < now,
                ),
            )
            .order_by(
                SecurityRateLimitModel.updated_at,
                SecurityRateLimitModel.kind,
                SecurityRateLimitModel.key_fingerprint,
            )
            .limit(limit),
            SecurityRateLimitKeyProjection,
        )
        keys = key_rows.all()
        if dry_run or not keys:
            return len(keys)
        deleted = 0
        for key in keys:
            result = await self._read_scalar(
                delete(SecurityRateLimitModel)
                .where(
                    SecurityRateLimitModel.kind == key.kind,
                    SecurityRateLimitModel.key_fingerprint == key.key_fingerprint,
                )
                .returning(SecurityRateLimitModel.key_fingerprint)
            )
            if result.one_or_none() is not None:
                deleted += 1
        return deleted

    async def cleanup_audit_events(
        self,
        *,
        cutoff: datetime,
        limit: int,
        dry_run: bool,
    ) -> int:
        """Delete only audit events older than the configured audit retention."""
        candidate_ids = await self._candidate_ids(
            select(AuditEventModel.id)
            .where(AuditEventModel.occurred_at < cutoff)
            .order_by(AuditEventModel.occurred_at, AuditEventModel.id)
            .limit(limit)
        )
        return await self._delete_ids(
            model=AuditEventModel,
            candidate_ids=candidate_ids,
            dry_run=dry_run,
        )

    async def _candidate_ids(self, statement: Select[tuple[UUID]]) -> list[UUID]:
        result = await self._read_scalar(statement)
        return result.all()

    async def _delete_ids(
        self,
        *,
        model: type[AuditEventModel]
        | type[RefreshTokenModel]
        | type[ServiceCredentialModel]
        | type[SessionModel],
        candidate_ids: list[UUID],
        dry_run: bool,
    ) -> int:
        if dry_run or not candidate_ids:
            return len(candidate_ids)
        result = await self._read_scalar(
            delete(model).where(model.id.in_(candidate_ids)).returning(model.id)
        )
        return len(result.all())

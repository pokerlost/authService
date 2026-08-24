"""SQLAlchemy PostgreSQL security rate-limit state repository."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert

from domain.enums import RateLimitKind
from persistence.database.models import SecurityRateLimitModel

from .base import SQLAlchemyRepository


class SQLAlchemySecurityRateLimitRepository(SQLAlchemyRepository):
    """Lock and mutate one multi-instance authentication attempt key."""

    async def get_for_update(
        self,
        *,
        kind: RateLimitKind,
        key_fingerprint: str,
    ) -> SecurityRateLimitModel | None:
        """Lock one existing limiter row for an atomic decision."""
        result = await self._read_scalar(
            select(SecurityRateLimitModel)
            .where(
                SecurityRateLimitModel.kind == kind,
                SecurityRateLimitModel.key_fingerprint == key_fingerprint,
            )
            .with_for_update(),
        )
        return result.one_or_none()

    async def create_if_absent(
        self,
        *,
        kind: RateLimitKind,
        key_fingerprint: str,
        window_started_at: datetime,
    ) -> SecurityRateLimitModel | None:
        """Create a zero-attempt window or return none after a concurrent insert."""
        result = await self._read_scalar(
            insert(SecurityRateLimitModel)
            .values(
                kind=kind,
                key_fingerprint=key_fingerprint,
                window_started_at=window_started_at,
                attempt_count=0,
                locked_until=None,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    SecurityRateLimitModel.kind,
                    SecurityRateLimitModel.key_fingerprint,
                ]
            )
            .returning(SecurityRateLimitModel),
        )
        return result.one_or_none()

    async def set_state(
        self,
        *,
        kind: RateLimitKind,
        key_fingerprint: str,
        window_started_at: datetime,
        attempt_count: int,
        locked_until: datetime | None,
    ) -> SecurityRateLimitModel:
        """Update and return one locked limiter row."""
        result = await self._read_scalar(
            update(SecurityRateLimitModel)
            .where(
                SecurityRateLimitModel.kind == kind,
                SecurityRateLimitModel.key_fingerprint == key_fingerprint,
            )
            .values(
                window_started_at=window_started_at,
                attempt_count=attempt_count,
                locked_until=locked_until,
            )
            .returning(SecurityRateLimitModel),
        )
        return result.one()

    async def clear(self, *, kind: RateLimitKind, key_fingerprint: str) -> None:
        """Remove obsolete failure state after successful authentication."""
        result = await self._read_scalar(
            delete(SecurityRateLimitModel)
            .where(
                SecurityRateLimitModel.kind == kind,
                SecurityRateLimitModel.key_fingerprint == key_fingerprint,
            )
            .returning(SecurityRateLimitModel.key_fingerprint),
        )
        result.one_or_none()

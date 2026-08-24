"""Atomic PostgreSQL-backed authentication rate-limit policy."""

from __future__ import annotations

from datetime import datetime, timedelta

from domain.enums import RateLimitKind
from domain.value_model import ValueModel
from persistence.repositories import SQLAlchemySecurityRateLimitRepository


class SecurityRateLimitPolicy(ValueModel):
    """One bounded authentication attempt window and temporary lock policy."""

    max_attempts: int
    window: timedelta
    lock: timedelta


class SecurityRateLimiter:
    """Serialize rate decisions through PostgreSQL row locks across instances."""

    __slots__ = ("_repository",)

    def __init__(self, repository: SQLAlchemySecurityRateLimitRepository) -> None:
        self._repository = repository

    async def is_limited(
        self,
        *,
        kind: RateLimitKind,
        key_fingerprint: str,
        now: datetime,
    ) -> bool:
        """Return whether a verified fingerprint remains temporarily locked."""
        state = await self._repository.get_for_update(
            kind=kind,
            key_fingerprint=key_fingerprint,
        )
        return state is not None and state.locked_until is not None and now < state.locked_until

    async def record_failure(
        self,
        *,
        kind: RateLimitKind,
        key_fingerprint: str,
        policy: SecurityRateLimitPolicy,
        now: datetime,
    ) -> bool:
        """Advance one atomic window and report whether the key is now locked."""
        state = await self._repository.get_for_update(
            kind=kind,
            key_fingerprint=key_fingerprint,
        )
        if state is None:
            state = await self._repository.create_if_absent(
                kind=kind,
                key_fingerprint=key_fingerprint,
                window_started_at=now,
            )
            if state is None:
                state = await self._repository.get_for_update(
                    kind=kind,
                    key_fingerprint=key_fingerprint,
                )
        if state is None:
            raise RuntimeError("Rate-limit row could not be locked")

        if now >= state.window_started_at + policy.window:
            window_started_at = now
            attempt_count = 1
        else:
            window_started_at = state.window_started_at
            attempt_count = state.attempt_count + 1
        locked_until = now + policy.lock if attempt_count >= policy.max_attempts else None
        await self._repository.set_state(
            kind=kind,
            key_fingerprint=key_fingerprint,
            window_started_at=window_started_at,
            attempt_count=attempt_count,
            locked_until=locked_until,
        )
        return locked_until is not None

    async def clear(self, *, kind: RateLimitKind, key_fingerprint: str) -> None:
        """Clear accumulated failures after successful credential authentication."""
        await self._repository.clear(kind=kind, key_fingerprint=key_fingerprint)

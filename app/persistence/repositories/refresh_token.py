"""SQLAlchemy refresh-token rotation repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import insert, select, update

from persistence.database.models import RefreshTokenModel

from .base import SQLAlchemyRepository


class SQLAlchemyRefreshTokenRepository(SQLAlchemyRepository):
    """Persist and serialize opaque refresh-token security transitions."""

    async def create(
        self,
        *,
        session_id: UUID,
        lookup_id: str,
        secret_digest: bytes,
        parent_token_id: UUID | None,
        expires_at: datetime,
    ) -> RefreshTokenModel:
        """Insert and return one digest-only refresh token."""
        result = await self._read_scalar(
            insert(RefreshTokenModel)
            .values(
                session_id=session_id,
                lookup_id=lookup_id,
                secret_digest=secret_digest,
                parent_token_id=parent_token_id,
                expires_at=expires_at,
            )
            .returning(RefreshTokenModel),
        )
        return result.one()

    async def get_by_lookup_id_for_update(self, lookup_id: str) -> RefreshTokenModel | None:
        """Lock and return one refresh row by its public locator."""
        result = await self._read_scalar(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.lookup_id == lookup_id)
            .with_for_update(),
        )
        return result.one_or_none()

    async def mark_consumed_and_replaced(
        self,
        *,
        token_id: UUID,
        consumed_at: datetime,
        replaced_by_token_id: UUID,
    ) -> RefreshTokenModel | None:
        """Consume one locked token and link its single replacement."""
        result = await self._read_scalar(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.id == token_id,
                RefreshTokenModel.consumed_at.is_(None),
                RefreshTokenModel.replaced_by_token_id.is_(None),
            )
            .values(
                consumed_at=consumed_at,
                replaced_by_token_id=replaced_by_token_id,
            )
            .returning(RefreshTokenModel),
        )
        return result.one_or_none()

    async def mark_reuse_detected(
        self,
        *,
        token_id: UUID,
        detected_at: datetime,
    ) -> RefreshTokenModel | None:
        """Record verified reuse of one previously consumed token."""
        result = await self._read_scalar(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(reuse_detected_at=detected_at)
            .returning(RefreshTokenModel),
        )
        return result.one_or_none()

    async def revoke_active_for_session(
        self,
        *,
        session_id: UUID,
        revoked_at: datetime,
    ) -> None:
        """Revoke every unconsumed refresh token in one session family."""
        result = await self._read_scalar(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.session_id == session_id,
                RefreshTokenModel.consumed_at.is_(None),
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
            .returning(RefreshTokenModel.id),
        )
        result.all()

    async def revoke_active_for_sessions(
        self,
        *,
        session_ids: list[UUID],
        revoked_at: datetime,
    ) -> None:
        """Revoke every unconsumed refresh token across the supplied session families."""
        if not session_ids:
            return
        result = await self._read_scalar(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.session_id.in_(session_ids),
                RefreshTokenModel.consumed_at.is_(None),
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
            .returning(RefreshTokenModel.id),
        )
        result.all()

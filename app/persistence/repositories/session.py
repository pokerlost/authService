"""SQLAlchemy human session repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import insert, select, update

from domain.enums import SessionRevocationReason, SessionStatus
from persistence.database.models import SessionModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemySessionRepository(SQLAlchemyEntityRepository[SessionModel]):
    """Persist and lock human sessions for security transitions."""

    model = SessionModel

    async def create(
        self,
        *,
        principal_id: UUID,
        status: SessionStatus,
        last_refreshed_at: datetime,
        idle_expires_at: datetime,
        absolute_expires_at: datetime,
    ) -> SessionModel:
        """Insert and return one human session."""
        result = await self._read_scalar(
            insert(SessionModel)
            .values(
                principal_id=principal_id,
                status=status,
                last_refreshed_at=last_refreshed_at,
                idle_expires_at=idle_expires_at,
                absolute_expires_at=absolute_expires_at,
            )
            .returning(SessionModel),
        )
        return result.one()

    async def get_by_id_for_update(self, session_id: UUID) -> SessionModel | None:
        """Lock and return one session for a serialized security mutation."""
        result = await self._read_scalar(
            select(SessionModel).where(SessionModel.id == session_id).with_for_update(),
        )
        return result.one_or_none()

    async def list_by_principal_id(self, principal_id: UUID) -> list[SessionModel]:
        """Return one principal's sessions in deterministic newest-first order."""
        result = await self._read_scalar(
            select(SessionModel)
            .where(SessionModel.principal_id == principal_id)
            .order_by(SessionModel.created_at.desc(), SessionModel.id.desc()),
        )
        return result.all()

    async def update_after_refresh(
        self,
        *,
        session_id: UUID,
        last_refreshed_at: datetime,
        idle_expires_at: datetime,
    ) -> SessionModel | None:
        """Advance only the idle portion of one active session lifetime."""
        result = await self._read_scalar(
            update(SessionModel)
            .where(
                SessionModel.id == session_id,
                SessionModel.status == SessionStatus.ACTIVE,
            )
            .values(
                last_refreshed_at=last_refreshed_at,
                idle_expires_at=idle_expires_at,
            )
            .returning(SessionModel),
        )
        return result.one_or_none()

    async def revoke(
        self,
        *,
        session_id: UUID,
        revoked_at: datetime,
        reason: SessionRevocationReason,
    ) -> SessionModel | None:
        """Revoke one currently active session without changing expiration."""
        result = await self._read_scalar(
            update(SessionModel)
            .where(
                SessionModel.id == session_id,
                SessionModel.status == SessionStatus.ACTIVE,
            )
            .values(
                status=SessionStatus.REVOKED,
                revoked_at=revoked_at,
                revocation_reason=reason,
            )
            .returning(SessionModel),
        )
        return result.one_or_none()

    async def revoke_all_active_for_principal(
        self,
        *,
        principal_id: UUID,
        revoked_at: datetime,
        reason: SessionRevocationReason,
    ) -> list[UUID]:
        """Revoke and return every active session ID owned by one principal."""
        result = await self._read_scalar(
            update(SessionModel)
            .where(
                SessionModel.principal_id == principal_id,
                SessionModel.status == SessionStatus.ACTIVE,
            )
            .values(
                status=SessionStatus.REVOKED,
                revoked_at=revoked_at,
                revocation_reason=reason,
            )
            .returning(SessionModel.id),
        )
        return result.all()

"""SQLAlchemy human session OAuth2 scope snapshot repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from persistence.database.models import SessionScopeModel

from .base import SQLAlchemyRepository


class SQLAlchemySessionScopeRepository(SQLAlchemyRepository):
    """Persist and read immutable original human session scope ceilings."""

    async def create_for_session(self, *, session_id: UUID, scopes: frozenset[str]) -> None:
        """Insert the complete immutable original scope ceiling."""
        if not scopes:
            return
        result = await self._read_scalar(
            insert(SessionScopeModel)
            .values(
                [{"session_id": session_id, "api_operation_id": scope} for scope in sorted(scopes)]
            )
            .returning(SessionScopeModel.api_operation_id),
        )
        result.all()

    async def list_for_session(self, session_id: UUID) -> list[SessionScopeModel]:
        """Return the immutable original scope ceiling in canonical order."""
        result = await self._read_scalar(
            select(SessionScopeModel)
            .where(SessionScopeModel.session_id == session_id)
            .order_by(SessionScopeModel.api_operation_id),
        )
        return result.all()

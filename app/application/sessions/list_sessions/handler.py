"""Owned session-list query orchestration."""

from __future__ import annotations

from persistence.repositories import SQLAlchemySessionRepository

from .query import ListSessionsQuery
from .result import ListSessionsResult
from .session_summary import SessionSummary


class ListSessionsHandler:
    """List only sessions owned by one authenticated principal."""

    __slots__ = ("_session_repository",)

    def __init__(self, session_repository: SQLAlchemySessionRepository) -> None:
        self._session_repository = session_repository

    async def execute(self, query: ListSessionsQuery) -> ListSessionsResult:
        """Return newest-first safe session summaries with one current marker."""
        sessions = await self._session_repository.list_by_principal_id(query.principal_id)
        return ListSessionsResult(
            sessions=[
                SessionSummary(
                    id=session.id,
                    status=session.status,
                    created_at=session.created_at,
                    last_refreshed_at=session.last_refreshed_at,
                    idle_expires_at=session.idle_expires_at,
                    absolute_expires_at=session.absolute_expires_at,
                    revoked_at=session.revoked_at,
                    current=session.id == query.current_session_id,
                )
                for session in sessions
            ],
        )

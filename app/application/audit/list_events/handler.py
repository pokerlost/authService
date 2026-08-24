"""Durable audit event page query handler."""

from __future__ import annotations

from persistence.queries import SQLAlchemyAuditEventQuery

from .query import ListAuditEventsQuery
from .result import AuditEventsPage


class ListAuditEventsHandler:
    """Read bounded immutable audit events using newest-first keyset pagination."""

    __slots__ = ("_query",)

    def __init__(self, query: SQLAlchemyAuditEventQuery) -> None:
        self._query = query

    async def execute(self, query: ListAuditEventsQuery) -> AuditEventsPage:
        """Return one page and an exclusive continuation cursor when more rows exist."""
        rows = await self._query.list_page(
            limit=query.limit + 1,
            before_occurred_at=query.before_occurred_at,
            before_id=query.before_id,
        )
        page_items = rows[: query.limit]
        if len(rows) <= query.limit or not page_items:
            return AuditEventsPage(items=page_items)
        last = page_items[-1]
        return AuditEventsPage(
            items=page_items,
            next_before_occurred_at=last.occurred_at,
            next_before_id=last.id,
        )

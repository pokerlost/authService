"""Durable audit read dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from api.dependencies import DatabaseSession
from application.audit import ListAuditEventsHandler
from persistence.queries import SQLAlchemyAuditEventQuery


def provide_list_audit_events_handler(session: DatabaseSession) -> ListAuditEventsHandler:
    """Compose bounded immutable audit event inspection."""
    return ListAuditEventsHandler(SQLAlchemyAuditEventQuery(session))


type ListAuditEventsHandlerDep = Annotated[
    ListAuditEventsHandler,
    Depends(provide_list_audit_events_handler),
]

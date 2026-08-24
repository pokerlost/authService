"""Owned session-list query."""

from __future__ import annotations

from uuid import UUID

from domain.value_model import ValueModel


class ListSessionsQuery(ValueModel):
    """Authenticated principal and current session list context."""

    principal_id: UUID
    current_session_id: UUID

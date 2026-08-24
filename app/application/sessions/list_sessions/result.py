"""Owned session-list result."""

from __future__ import annotations

from domain.value_model import ValueModel

from .session_summary import SessionSummary


class ListSessionsResult(ValueModel):
    """Deterministically ordered safe session summaries."""

    sessions: list[SessionSummary]

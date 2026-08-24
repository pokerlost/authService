"""Bounded security-state cleanup result."""

from __future__ import annotations

from domain.value_model import ValueModel


class CleanupSummary(ValueModel):
    """Exact selected or deleted row counts from one bounded cleanup pass."""

    dry_run: bool
    refresh_tokens: int
    sessions: int
    service_credentials: int
    rate_limit_rows: int
    audit_events: int

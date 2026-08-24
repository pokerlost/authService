"""Bounded security-state cleanup command."""

from __future__ import annotations

from pydantic import Field

from domain.value_model import ValueModel


class CleanupSecurityStateCommand(ValueModel):
    """Configured retention bounds and dry-run policy for one cleanup pass."""

    batch_size: int = Field(ge=1, le=10_000)
    security_state_retention_days: int = Field(ge=1, le=3_650)
    audit_retention_days: int = Field(ge=30, le=3_650)
    dry_run: bool = True

"""Security-state cleanup and audit retention settings."""

from __future__ import annotations

from pydantic import Field

from .base import SettingsModel


class MaintenanceSettings(SettingsModel):
    """Bound cleanup batches and retention thresholds."""

    cleanup_batch_size: int = Field(default=500, ge=1, le=10_000)
    security_state_retention_days: int = Field(default=30, ge=1, le=3_650)
    audit_retention_days: int = Field(default=365, ge=30, le=3_650)

"""Support-safe ordinary-user account details."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.enums import PrincipalStatus
from domain.value_model import ValueModel


class UserAccountDetails(ValueModel):
    """Minimal ordinary-user identity and authentication status safe for staff."""

    id: UUID
    username: str
    nickname: str
    status: PrincipalStatus
    created_at: datetime

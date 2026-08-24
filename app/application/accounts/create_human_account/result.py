"""Created human account result."""

from __future__ import annotations

from uuid import UUID

from domain.enums import Role
from domain.value_model import ValueModel


class CreatedHumanAccount(ValueModel):
    """Safe identity returned by trusted human account provisioning."""

    id: UUID
    username: str
    nickname: str
    role: Role

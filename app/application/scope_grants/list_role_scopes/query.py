"""Role scope list query."""

from __future__ import annotations

from pydantic import Field

from domain.value_model import ValueModel


class ListRoleScopesQuery(ValueModel):
    """Bounded role scope list request."""

    limit: int = Field(ge=1, le=10_000)

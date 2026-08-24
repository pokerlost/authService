"""Get OpenAPI contract query."""

from __future__ import annotations

from uuid import UUID

from domain.value_model import ValueModel


class GetOpenAPIContractQuery(ValueModel):
    """Explicit immutable contract selected for master inspection."""

    contract_id: UUID

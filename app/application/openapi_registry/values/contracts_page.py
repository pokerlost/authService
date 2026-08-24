"""Bounded OpenAPI contract keyset page."""

from __future__ import annotations

from uuid import UUID

from domain.value_model import ValueModel

from .contract_summary import OpenAPIContractSummary


class OpenAPIContractsPage(ValueModel):
    """One deterministic contract page and the next UUID cursor when present."""

    items: list[OpenAPIContractSummary]
    next_cursor: UUID | None

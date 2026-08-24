"""Diff validated OpenAPI contract query."""

from __future__ import annotations

from uuid import UUID

from domain.value_model import ValueModel


class DiffOpenAPIContractQuery(ValueModel):
    """Candidate contract compared with its service's active base."""

    contract_id: UUID

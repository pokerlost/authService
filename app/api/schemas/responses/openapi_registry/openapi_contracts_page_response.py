"""OpenAPI contracts page response schema."""

from __future__ import annotations

from uuid import UUID

from api.schemas.base import ResponseModel

from .openapi_contract_summary_response import OpenApiContractSummaryResponse


class OpenApiContractsPageResponse(ResponseModel):
    """Bounded deterministic contract list and optional UUID keyset cursor."""

    items: list[OpenApiContractSummaryResponse]
    next_cursor: UUID | None

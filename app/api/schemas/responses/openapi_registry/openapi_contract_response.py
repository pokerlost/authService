"""OpenAPI contract detail response schema."""

from __future__ import annotations

from .openapi_contract_summary_response import OpenApiContractSummaryResponse


class OpenApiContractResponse(OpenApiContractSummaryResponse):
    """Explicit master detail including immutable submitted JSON."""

    document: dict[str, object]

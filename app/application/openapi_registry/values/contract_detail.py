"""OpenAPI contract explicit detail result."""

from __future__ import annotations

from .contract_summary import OpenAPIContractSummary


class OpenAPIContractDetail(OpenAPIContractSummary):
    """Control-plane summary plus the immutable submitted JSON document."""

    document: dict[str, object]

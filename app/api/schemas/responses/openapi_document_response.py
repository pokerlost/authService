"""Public JSON OpenAPI document response."""

from __future__ import annotations

from api.schemas.base import ResponseModel


class OpenApiDocumentResponse(ResponseModel):
    """JSON-compatible generated OpenAPI document inside ApplicationResponse."""

    document: dict[str, object]

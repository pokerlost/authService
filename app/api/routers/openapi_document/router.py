"""Wrapped public OpenAPI JSON publication RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.openapi import OpenAPITag
from api.schemas.responses import ApplicationResponse, OpenApiDocumentResponse
from api.types import HandlerResult

router = APIRouter(tags=[OpenAPITag.OPENAPI])


@router.get(
    path="/openapi.get",
    response_model=ApplicationResponse[OpenApiDocumentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get the OpenAPI JSON document",
    description="Return the generated authService OpenAPI contract as a wrapped JSON object.",
    operation_id="authService.openapi.get",
    openapi_extra={"security": []},
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[OpenApiDocumentResponse]
        },
    },
)
def get_openapi_document(request: Request) -> HandlerResult:
    """Return only the JSON-compatible generated contract inside the universal envelope."""
    return {
        "ok": True,
        "result": {"document": request.app.openapi()},
    }

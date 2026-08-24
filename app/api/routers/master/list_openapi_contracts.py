"""Master OpenAPI contract list RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import ListOpenAPIContractsRequest
from api.schemas.responses import ApplicationResponse, OpenApiContractsPageResponse
from api.types import HandlerResult

from .openapi_registry_dependencies import ListOpenAPIContractsHandlerDep
from .security_dependencies import ListOpenApiContractsPrincipalDep

router = APIRouter()


@router.post(
    path=".listOpenApiContracts",
    response_model=ApplicationResponse[OpenApiContractsPageResponse],
    status_code=status.HTTP_200_OK,
    summary="List OpenAPI contracts",
    description="Return a bounded UUID-keyset contract summary page without submitted JSON.",
    operation_id="authService.master.listOpenApiContracts",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[OpenApiContractsPageResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[OpenApiContractsPageResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[OpenApiContractsPageResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[OpenApiContractsPageResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[OpenApiContractsPageResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[OpenApiContractsPageResponse]
        },
    },
)
async def list_openapi_contracts(
    request: ListOpenAPIContractsRequest,
    _principal: ListOpenApiContractsPrincipalDep,
    handler: ListOpenAPIContractsHandlerDep,
) -> HandlerResult:
    """List immutable summaries for one exact registered service."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

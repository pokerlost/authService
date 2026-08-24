"""Master OpenAPI contract detail RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import OpenAPIContractRequest
from api.schemas.responses import ApplicationResponse, OpenApiContractResponse
from api.types import HandlerResult
from application.openapi_registry import GetOpenAPIContractQuery

from .openapi_registry_dependencies import GetOpenAPIContractHandlerDep
from .security_dependencies import GetOpenApiContractPrincipalDep

router = APIRouter()


@router.post(
    path=".getOpenApiContract",
    response_model=ApplicationResponse[OpenApiContractResponse],
    status_code=status.HTTP_200_OK,
    summary="Get OpenAPI contract",
    description="Return one scope-protected contract detail including immutable JSON.",
    operation_id="authService.master.getOpenApiContract",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[OpenApiContractResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[OpenApiContractResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[OpenApiContractResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[OpenApiContractResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[OpenApiContractResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[OpenApiContractResponse]
        },
    },
)
async def get_openapi_contract(
    request: OpenAPIContractRequest,
    _principal: GetOpenApiContractPrincipalDep,
    handler: GetOpenAPIContractHandlerDep,
) -> HandlerResult:
    """Return raw JSON only for an explicitly selected persisted contract."""
    result = await handler.execute(GetOpenAPIContractQuery(contract_id=request.contract_id))
    return {
        "ok": True,
        "result": result,
    }

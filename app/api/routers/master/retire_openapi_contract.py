"""Master OpenAPI contract retirement RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import OpenAPIContractRequest
from api.schemas.responses import ApplicationResponse, OpenApiContractSummaryResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.openapi_registry import RetireOpenAPIContractCommand

from .openapi_registry_dependencies import RetireOpenAPIContractHandlerDep
from .security_dependencies import RetireOpenApiContractPrincipalDep

router = APIRouter()


@router.post(
    path=".retireOpenApiContract",
    response_model=ApplicationResponse[OpenApiContractSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Retire OpenAPI contract",
    description=(
        "Retire an active or validated-never-active contract without deleting history or "
        "ownership."
    ),
    operation_id="authService.master.retireOpenApiContract",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ApplicationResponse[OpenApiContractSummaryResponse]
        },
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[OpenApiContractSummaryResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[OpenApiContractSummaryResponse]},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse[OpenApiContractSummaryResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[OpenApiContractSummaryResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[OpenApiContractSummaryResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[OpenApiContractSummaryResponse]
        },
    },
)
async def retire_openapi_contract(
    request: Request,
    body: OpenAPIContractRequest,
    principal: RetireOpenApiContractPrincipalDep,
    handler: RetireOpenAPIContractHandlerDep,
) -> HandlerResult:
    """Retire explicit active or validated history idempotently."""
    result = await handler.execute(
        RetireOpenAPIContractCommand(
            contract_id=body.contract_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.retireOpenApiContract",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": result,
    }

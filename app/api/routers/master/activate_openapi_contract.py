"""Master OpenAPI contract activation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ActivateOpenAPIContractRequest
from api.schemas.responses import ApplicationResponse, OpenApiContractSummaryResponse
from api.types import HandlerResult
from application.audit import AuditContext

from .openapi_registry_dependencies import ActivateOpenAPIContractHandlerDep
from .security_dependencies import ActivateOpenApiContractPrincipalDep

router = APIRouter()


@router.post(
    path=".activateOpenApiContract",
    response_model=ApplicationResponse[OpenApiContractSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Activate OpenAPI contract",
    description=(
        "Atomically verify base, diff, acknowledgement, and ownership before replacing "
        "active state."
    ),
    operation_id="authService.master.activateOpenApiContract",
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
async def activate_openapi_contract(
    request: Request,
    body: ActivateOpenAPIContractRequest,
    principal: ActivateOpenApiContractPrincipalDep,
    handler: ActivateOpenAPIContractHandlerDep,
) -> HandlerResult:
    """Apply an explicit optimistic activation without silent rebasing."""
    result = await handler.execute(
        body.to_command(
            AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.activateOpenApiContract",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            )
        )
    )
    return {
        "ok": True,
        "result": result,
    }

"""Master OpenAPI contract validation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import OpenAPIContractRequest
from api.schemas.responses import ApplicationResponse, ValidationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.openapi_registry import ValidateOpenAPIContractCommand

from .openapi_registry_dependencies import ValidateOpenAPIContractHandlerDep
from .security_dependencies import ValidateOpenApiContractPrincipalDep

router = APIRouter()


@router.post(
    path=".validateOpenApiContract",
    response_model=ApplicationResponse[ValidationResponse],
    status_code=status.HTTP_200_OK,
    summary="Validate OpenAPI contract",
    description=(
        "Validate fail-closed and atomically persist normalized operations and policies only "
        "when valid."
    ),
    operation_id="authService.master.validateOpenApiContract",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[ValidationResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[ValidationResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[ValidationResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse[ValidationResponse]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse[ValidationResponse]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[ValidationResponse]},
    },
)
async def validate_openapi_contract(
    request: Request,
    body: OpenAPIContractRequest,
    principal: ValidateOpenApiContractPrincipalDep,
    handler: ValidateOpenAPIContractHandlerDep,
) -> HandlerResult:
    """Return a typed issue report and never leave partial normalized state."""
    result = await handler.execute(
        ValidateOpenAPIContractCommand(
            contract_id=body.contract_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.validateOpenApiContract",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": result,
    }

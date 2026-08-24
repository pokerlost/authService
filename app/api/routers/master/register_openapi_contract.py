"""Master OpenAPI contract registration RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import RegisterOpenAPIContractRequest
from api.schemas.responses import ApplicationResponse, RegisteredOpenApiContractResponse
from api.types import HandlerResult
from application.audit import AuditContext

from .openapi_registry_dependencies import RegisterOpenAPIContractHandlerDep
from .security_dependencies import RegisterOpenApiContractPrincipalDep

router = APIRouter()


@router.post(
    path=".registerOpenApiContract",
    response_model=ApplicationResponse[RegisteredOpenApiContractResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register OpenAPI contract",
    description=(
        "Persist one bounded immutable OpenAPI JSON contract without validating or activating it."
    ),
    operation_id="authService.master.registerOpenApiContract",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ApplicationResponse[RegisteredOpenApiContractResponse]
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ApplicationResponse[RegisteredOpenApiContractResponse]
        },
        status.HTTP_409_CONFLICT: {
            "model": ApplicationResponse[RegisteredOpenApiContractResponse]
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[RegisteredOpenApiContractResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[RegisteredOpenApiContractResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[RegisteredOpenApiContractResponse]
        },
    },
)
async def register_openapi_contract(
    request: Request,
    body: RegisterOpenAPIContractRequest,
    principal: RegisterOpenApiContractPrincipalDep,
    handler: RegisterOpenAPIContractHandlerDep,
) -> HandlerResult:
    """Register a contract with service ID and version extracted only from its document."""
    result = await handler.execute(
        body.to_command(
            AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.registerOpenApiContract",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            )
        )
    )
    return {
        "ok": True,
        "result": result,
    }

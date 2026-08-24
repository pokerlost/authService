"""Master AUTO principal creation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceIdentityRequest
from api.schemas.responses import ApplicationResponse, AutoPrincipalResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.service_authentication import CreateServicePrincipalCommand

from .security_dependencies import CreateAutoPrincipalPrincipalDep
from .service_authentication_dependencies import CreateServicePrincipalHandlerDep

router = APIRouter()


@router.post(
    path=".createAutoPrincipal",
    response_model=ApplicationResponse[AutoPrincipalResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create AUTO principal",
    description=(
        "Create one active AUTO principal through the accepted operator application handler."
    ),
    operation_id="authService.master.createAutoPrincipal",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[AutoPrincipalResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[AutoPrincipalResponse]},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse[AutoPrincipalResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[AutoPrincipalResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[AutoPrincipalResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[AutoPrincipalResponse]},
    },
)
async def create_auto_principal(
    request: Request,
    body: ServiceIdentityRequest,
    principal: CreateAutoPrincipalPrincipalDep,
    handler: CreateServicePrincipalHandlerDep,
) -> HandlerResult:
    """Reuse AUTO CLI provisioning behavior behind exact master authorization."""
    service_principal = await handler.execute(
        CreateServicePrincipalCommand(
            service_slug=body.service_slug,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.createAutoPrincipal",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": {
            "principal_id": service_principal.principal_id,
            "service_slug": service_principal.service_slug,
            "created_at": service_principal.created_at,
        },
    }

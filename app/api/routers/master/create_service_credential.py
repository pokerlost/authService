"""Master one-time service credential creation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceIdentityRequest
from api.schemas.responses import ApplicationResponse, ServiceCredentialResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.service_authentication import CreateServiceCredentialCommand

from .security_dependencies import CreateServiceCredentialPrincipalDep
from .service_authentication_dependencies import CreateServiceCredentialHandlerDep

router = APIRouter()


@router.post(
    path=".createServiceCredential",
    response_model=ApplicationResponse[ServiceCredentialResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create service credential",
    description=(
        "Create one parallel rotatable credential and disclose its raw secret exactly once."
    ),
    operation_id="authService.master.createServiceCredential",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[ServiceCredentialResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[ServiceCredentialResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[ServiceCredentialResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[ServiceCredentialResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[ServiceCredentialResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[ServiceCredentialResponse]
        },
    },
)
async def create_service_credential(
    request: Request,
    body: ServiceIdentityRequest,
    principal: CreateServiceCredentialPrincipalDep,
    handler: CreateServiceCredentialHandlerDep,
) -> HandlerResult:
    """Intentionally unwrap the generated secret only into this one explicit response."""
    credential = await handler.execute(
        CreateServiceCredentialCommand(
            service_slug=body.service_slug,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.createServiceCredential",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": {
            "client_id": credential.client_id,
            "client_secret": credential.client_secret.get_secret_value(),
            "expires_at": credential.expires_at,
        },
    }

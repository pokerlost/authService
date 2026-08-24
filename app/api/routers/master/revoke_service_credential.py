"""Master service credential revocation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceCredentialRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.service_authentication import RevokeServiceCredentialCommand

from .security_dependencies import RevokeServiceCredentialPrincipalDep
from .service_authentication_dependencies import RevokeServiceCredentialHandlerDep

router = APIRouter()


@router.post(
    path=".revokeServiceCredential",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke service credential",
    description=(
        "Idempotently revoke one known client ID without invalidating already-issued JWTs."
    ),
    operation_id="authService.master.revokeServiceCredential",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def revoke_service_credential(
    request: Request,
    body: ServiceCredentialRequest,
    principal: RevokeServiceCredentialPrincipalDep,
    handler: RevokeServiceCredentialHandlerDep,
) -> HandlerResult:
    """Reuse the accepted digest-only credential revocation handler."""
    await handler.execute(
        RevokeServiceCredentialCommand(
            client_id=body.client_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.revokeServiceCredential",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }

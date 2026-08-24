"""Master-authorized human account disable RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import AccountStatusRequest
from api.schemas.responses import AccountStatusResponse, ApplicationResponse
from api.types import HandlerResult
from application.accounts import DisableHumanAccountCommand
from application.audit import AuditContext

from .dependencies import DisableHumanAccountHandlerDep
from .security_dependencies import DisableAccountPrincipalDep

router = APIRouter()


@router.post(
    path=".disableAccount",
    response_model=ApplicationResponse[AccountStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Disable human account",
    description="Disable one human principal and revoke its active session families.",
    operation_id="authService.master.disableAccount",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[AccountStatusResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[AccountStatusResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[AccountStatusResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[AccountStatusResponse],
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[AccountStatusResponse],
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[AccountStatusResponse],
        },
    },
)
async def disable_account(
    request: Request,
    body: AccountStatusRequest,
    principal: DisableAccountPrincipalDep,
    handler: DisableHumanAccountHandlerDep,
) -> HandlerResult:
    """Disable a non-current human target using trusted actor identity."""
    target = await handler.execute(
        DisableHumanAccountCommand(
            target_principal_id=body.principal_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.disableAccount",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        ),
    )
    return {
        "ok": True,
        "result": {
            "principal_id": target.id,
            "status": target.status,
        },
    }

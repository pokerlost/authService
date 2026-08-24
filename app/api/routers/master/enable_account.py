"""Master-authorized human account enable RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import AccountStatusRequest
from api.schemas.responses import AccountStatusResponse, ApplicationResponse
from api.types import HandlerResult
from application.accounts import EnableHumanAccountCommand
from application.audit import AuditContext

from .dependencies import EnableHumanAccountHandlerDep
from .security_dependencies import EnableAccountPrincipalDep

router = APIRouter()


@router.post(
    path=".enableAccount",
    response_model=ApplicationResponse[AccountStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Enable human account",
    description="Enable one human principal without restoring any revoked session state.",
    operation_id="authService.master.enableAccount",
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
async def enable_account(
    request: Request,
    body: AccountStatusRequest,
    principal: EnableAccountPrincipalDep,
    handler: EnableHumanAccountHandlerDep,
) -> HandlerResult:
    """Enable a human target after exact master authorization."""
    target = await handler.execute(
        EnableHumanAccountCommand(
            target_principal_id=body.principal_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.enableAccount",
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

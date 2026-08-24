"""Master-assisted human password reset RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ResetHumanPasswordRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.accounts import ResetHumanPasswordCommand
from application.audit import AuditContext

from .dependencies import ResetHumanPasswordHandlerDep
from .security_dependencies import ResetHumanPasswordPrincipalDep

router = APIRouter()


@router.post(
    path=".resetHumanPassword",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset a human password",
    description="Replace a distinct human credential and revoke all target sessions.",
    operation_id="authService.master.resetHumanPassword",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def reset_human_password(
    request: Request,
    body: ResetHumanPasswordRequest,
    principal: ResetHumanPasswordPrincipalDep,
    handler: ResetHumanPasswordHandlerDep,
) -> HandlerResult:
    """Replace a target password using the exact reset operation scope."""
    await handler.execute(
        ResetHumanPasswordCommand(
            target_principal_id=body.principal_id,
            new_password=body.new_password,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.resetHumanPassword",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }

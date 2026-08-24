"""Master-authorized support account creation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import CreateStaffAccountRequest
from api.schemas.responses import AccountResponse, ApplicationResponse
from api.types import HandlerResult
from application.accounts import CreateHumanAccountCommand
from application.audit import AuditContext
from domain.enums import Role

from .dependencies import CreateHumanAccountHandlerDep
from .security_dependencies import CreateSupportAccountPrincipalDep

router = APIRouter()


@router.post(
    path=".createSupportAccount",
    response_model=ApplicationResponse[AccountResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create support account",
    description="Create one separate active support staff identity with a direct support role.",
    operation_id="authService.master.createSupportAccount",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[AccountResponse]},
    },
)
async def create_support_account(
    request: Request,
    body: CreateStaffAccountRequest,
    principal: CreateSupportAccountPrincipalDep,
    handler: CreateHumanAccountHandlerDep,
) -> HandlerResult:
    """Create support with a server-controlled role after exact operation-scope authorization."""
    result = await handler.execute(
        CreateHumanAccountCommand(
            username=body.username,
            nickname=body.nickname,
            password=body.password,
            role=Role.SUPPORT,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.createSupportAccount",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        ),
    )
    return {
        "ok": True,
        "result": result,
    }

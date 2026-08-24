"""Support-safe ordinary-user account lookup RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import GetUserAccountRequest
from api.schemas.responses import ApplicationResponse, SupportUserAccountResponse
from api.types import HandlerResult

from .dependencies import GetUserAccountHandlerDep, GetUserAccountPrincipalDep

router = APIRouter()


@router.post(
    path=".getUserAccount",
    response_model=ApplicationResponse[SupportUserAccountResponse],
    status_code=status.HTTP_200_OK,
    summary="Get ordinary-user account for support",
    description="Return a bounded safe view after exact support-operation scope authorization.",
    operation_id="authService.support.getUserAccount",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ApplicationResponse[SupportUserAccountResponse],
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ApplicationResponse[SupportUserAccountResponse],
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ApplicationResponse[SupportUserAccountResponse],
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[SupportUserAccountResponse],
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[SupportUserAccountResponse],
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[SupportUserAccountResponse],
        },
    },
)
async def get_user_account(
    request: GetUserAccountRequest,
    principal: GetUserAccountPrincipalDep,
    handler: GetUserAccountHandlerDep,
) -> HandlerResult:
    """Return ordinary-user data only after exact operation-scope authorization."""
    result = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": result,
    }

"""Master direct role scope list RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.responses import ApplicationResponse, RoleScopesResponse
from api.types import HandlerResult
from application.scope_grants import ListRoleScopesQuery

from .scope_grant_dependencies import ListRoleScopesHandlerDep, ScopeGrantListLimitDep
from .security_dependencies import ListRoleScopesPrincipalDep

router = APIRouter()


@router.get(
    path=".listRoleScopes",
    response_model=ApplicationResponse[RoleScopesResponse],
    status_code=status.HTTP_200_OK,
    summary="List role scopes",
    description="List bounded explicit direct role scope grants without inheritance.",
    operation_id="authService.master.listRoleScopes",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[RoleScopesResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[RoleScopesResponse]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse[RoleScopesResponse]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[RoleScopesResponse]},
    },
)
async def list_role_scopes(
    _principal: ListRoleScopesPrincipalDep,
    handler: ListRoleScopesHandlerDep,
    limit: ScopeGrantListLimitDep,
) -> HandlerResult:
    """Return a bounded deterministic direct role grant list."""
    grants = await handler.execute(ListRoleScopesQuery(limit=limit))
    return {
        "ok": True,
        "result": {
            "items": [
                {
                    "role": grant.role,
                    "scope": grant.api_operation_id,
                    "created_at": grant.created_at,
                }
                for grant in grants
            ]
        },
    }

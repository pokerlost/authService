"""Master service scope list RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import ListServiceScopesRequest
from api.schemas.responses import ApplicationResponse, ServiceScopesResponse
from api.types import HandlerResult
from application.scope_grants import ListServiceScopesQuery

from .scope_grant_dependencies import ListServiceScopesHandlerDep, ScopeGrantListLimitDep
from .security_dependencies import ListServiceScopesPrincipalDep

router = APIRouter()


@router.post(
    path=".listServiceScopes",
    response_model=ApplicationResponse[ServiceScopesResponse],
    status_code=status.HTTP_200_OK,
    summary="List service scopes",
    description="List bounded exact grants for one source service and target resource.",
    operation_id="authService.master.listServiceScopes",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[ServiceScopesResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[ServiceScopesResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[ServiceScopesResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[ServiceScopesResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[ServiceScopesResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[ServiceScopesResponse]},
    },
)
async def list_service_scopes(
    body: ListServiceScopesRequest,
    _principal: ListServiceScopesPrincipalDep,
    handler: ListServiceScopesHandlerDep,
    limit: ScopeGrantListLimitDep,
) -> HandlerResult:
    """Return one bounded deterministic source and audience grant list."""
    grants = await handler.execute(
        ListServiceScopesQuery(
            service_slug=body.service_slug,
            audience=body.audience,
            limit=limit,
        )
    )
    return {
        "ok": True,
        "result": {
            "items": [
                {
                    "service_principal_id": grant.service_principal_id,
                    "audience": grant.audience,
                    "scope": grant.api_operation_id,
                    "created_at": grant.created_at,
                }
                for grant in grants
            ]
        },
    }

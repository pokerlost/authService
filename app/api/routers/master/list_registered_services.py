"""Master registered-service list RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.responses import ApplicationResponse, RegisteredServicesPageResponse
from api.types import HandlerResult
from application.openapi_registry import ListRegisteredServicesQuery

from .openapi_registry_dependencies import (
    ListRegisteredServicesHandlerDep,
    RegisteredServiceListCursor,
    RegisteredServiceListLimit,
)
from .security_dependencies import ListRegisteredServicesPrincipalDep

router = APIRouter()


@router.get(
    path=".listRegisteredServices",
    response_model=ApplicationResponse[RegisteredServicesPageResponse],
    status_code=status.HTTP_200_OK,
    summary="List registered services",
    description="Return one bounded service-ID keyset page from the OpenAPI control plane.",
    operation_id="authService.master.listRegisteredServices",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ApplicationResponse[RegisteredServicesPageResponse]
        },
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[RegisteredServicesPageResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[RegisteredServicesPageResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[RegisteredServicesPageResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[RegisteredServicesPageResponse]
        },
    },
)
async def list_registered_services(
    _principal: ListRegisteredServicesPrincipalDep,
    handler: ListRegisteredServicesHandlerDep,
    limit: RegisteredServiceListLimit = 50,
    after_service_id: RegisteredServiceListCursor = None,
) -> HandlerResult:
    """Use the sole deliberate bounded GET query-parameter exception for registry paging."""
    result = await handler.execute(
        ListRegisteredServicesQuery(
            limit=limit,
            after_service_id=after_service_id,
        )
    )
    return {
        "ok": True,
        "result": result,
    }

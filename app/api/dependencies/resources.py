"""Runtime resource dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from api.resources import ApplicationResources
from application.idempotency import BusinessOperationFingerprinter
from application.ports import ServiceAccessTokenSigner


def _resolve_application_resources(request: Request) -> ApplicationResources:
    """Return lifespan-owned application resources."""
    resources = request.app.state.resources
    if not isinstance(resources, ApplicationResources):
        raise RuntimeError("Application resources are not initialized")
    return resources


type ApplicationResourcesDep = Annotated[
    ApplicationResources,
    Depends(_resolve_application_resources),
]


def _resolve_business_operation_fingerprinter(
    resources: ApplicationResourcesDep,
) -> BusinessOperationFingerprinter:
    """Return the lifespan-owned business-operation fingerprinter."""
    return resources.business_operation_fingerprinter


type BusinessOperationFingerprinterDep = Annotated[
    BusinessOperationFingerprinter,
    Depends(_resolve_business_operation_fingerprinter),
]


def _resolve_service_access_token_signer(
    resources: ApplicationResourcesDep,
) -> ServiceAccessTokenSigner:
    """Return the lifespan-owned service access-token signer."""
    return resources.service_access_token_signer


type ServiceAccessTokenSignerDep = Annotated[
    ServiceAccessTokenSigner,
    Depends(_resolve_service_access_token_signer),
]

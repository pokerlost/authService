"""Master OpenAPI registry dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query

from api.dependencies import ApplicationResourcesDep, DatabaseSession, SettingsDep
from application.audit import DurableAuditFailureRecorder
from application.openapi_registry import (
    ActivateOpenAPIContractHandler,
    DiffOpenAPIContractHandler,
    GetAuthorizationManifestHandler,
    GetOpenAPIContractHandler,
    GetRegisteredServiceHandler,
    ListOpenAPIContractsHandler,
    ListRegisteredServicesHandler,
    OpenAPIContractAnalyzer,
    OpenAPIContractDiffCalculator,
    RegisterOpenAPIContractHandler,
    RetireOpenAPIContractHandler,
    ValidateOpenAPIContractHandler,
)
from domain.types import ServiceId
from persistence.queries import SQLAlchemyOpenAPIRegistryQuery
from persistence.repositories import (
    SQLAlchemyAPIOperationRepository,
    SQLAlchemyAuditEventRepository,
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyOperationIdentityRepository,
    SQLAlchemyRegisteredServiceRepository,
)


def provide_register_openapi_contract_handler(
    session: DatabaseSession,
    settings: SettingsDep,
) -> RegisterOpenAPIContractHandler:
    """Compose immutable registration with configured hostile-input limits."""
    return RegisterOpenAPIContractHandler(
        analyzer=OpenAPIContractAnalyzer(settings.openapi_registry),
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RegisterOpenAPIContractHandlerDep = Annotated[
    RegisterOpenAPIContractHandler,
    Depends(provide_register_openapi_contract_handler),
]


def provide_validate_openapi_contract_handler(
    session: DatabaseSession,
    settings: SettingsDep,
) -> ValidateOpenAPIContractHandler:
    """Compose validation, ownership checks, and atomic normalized persistence."""
    return ValidateOpenAPIContractHandler(
        analyzer=OpenAPIContractAnalyzer(settings.openapi_registry),
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
        operation_repository=SQLAlchemyAPIOperationRepository(session),
        operation_identity_repository=SQLAlchemyOperationIdentityRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type ValidateOpenAPIContractHandlerDep = Annotated[
    ValidateOpenAPIContractHandler,
    Depends(provide_validate_openapi_contract_handler),
]


def provide_diff_openapi_contract_handler(
    session: DatabaseSession,
) -> DiffOpenAPIContractHandler:
    """Compose deterministic normalized contract diff calculation."""
    return DiffOpenAPIContractHandler(
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
        registry_query=SQLAlchemyOpenAPIRegistryQuery(session),
        calculator=OpenAPIContractDiffCalculator(),
    )


type DiffOpenAPIContractHandlerDep = Annotated[
    DiffOpenAPIContractHandler,
    Depends(provide_diff_openapi_contract_handler),
]


def provide_activate_openapi_contract_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
) -> ActivateOpenAPIContractHandler:
    """Compose locked activation, diff verification, and permanent ownership claims."""
    return ActivateOpenAPIContractHandler(
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
        operation_identity_repository=SQLAlchemyOperationIdentityRepository(session),
        registry_query=SQLAlchemyOpenAPIRegistryQuery(session),
        calculator=OpenAPIContractDiffCalculator(),
        audit_repository=SQLAlchemyAuditEventRepository(session),
        failure_audit_recorder=DurableAuditFailureRecorder(resources.session_factory),
    )


type ActivateOpenAPIContractHandlerDep = Annotated[
    ActivateOpenAPIContractHandler,
    Depends(provide_activate_openapi_contract_handler),
]


def provide_retire_openapi_contract_handler(
    session: DatabaseSession,
) -> RetireOpenAPIContractHandler:
    """Compose serialized explicit contract retirement."""
    return RetireOpenAPIContractHandler(
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RetireOpenAPIContractHandlerDep = Annotated[
    RetireOpenAPIContractHandler,
    Depends(provide_retire_openapi_contract_handler),
]


def provide_list_registered_services_handler(
    session: DatabaseSession,
) -> ListRegisteredServicesHandler:
    """Compose bounded registered-service read queries."""
    return ListRegisteredServicesHandler(SQLAlchemyOpenAPIRegistryQuery(session))


type ListRegisteredServicesHandlerDep = Annotated[
    ListRegisteredServicesHandler,
    Depends(provide_list_registered_services_handler),
]

type RegisteredServiceListLimit = Annotated[
    int,
    Query(ge=1, le=100, description="Maximum registered services to return."),
]

type RegisteredServiceListCursor = Annotated[
    ServiceId | None,
    Query(
        alias="afterServiceId",
        description="Exclusive service-ID keyset cursor.",
    ),
]


def provide_get_registered_service_handler(
    session: DatabaseSession,
) -> GetRegisteredServiceHandler:
    """Compose exact registered-service lookup."""
    return GetRegisteredServiceHandler(SQLAlchemyRegisteredServiceRepository(session))


type GetRegisteredServiceHandlerDep = Annotated[
    GetRegisteredServiceHandler,
    Depends(provide_get_registered_service_handler),
]


def provide_list_openapi_contracts_handler(
    session: DatabaseSession,
) -> ListOpenAPIContractsHandler:
    """Compose bounded contract summary read queries."""
    return ListOpenAPIContractsHandler(
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        registry_query=SQLAlchemyOpenAPIRegistryQuery(session),
    )


type ListOpenAPIContractsHandlerDep = Annotated[
    ListOpenAPIContractsHandler,
    Depends(provide_list_openapi_contracts_handler),
]


def provide_get_openapi_contract_handler(
    session: DatabaseSession,
) -> GetOpenAPIContractHandler:
    """Compose explicit immutable contract detail lookup."""
    return GetOpenAPIContractHandler(
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
    )


type GetOpenAPIContractHandlerDep = Annotated[
    GetOpenAPIContractHandler,
    Depends(provide_get_openapi_contract_handler),
]


def provide_get_authorization_manifest_handler(
    session: DatabaseSession,
) -> GetAuthorizationManifestHandler:
    """Compose active-only normalized authorization manifest lookup."""
    return GetAuthorizationManifestHandler(
        service_repository=SQLAlchemyRegisteredServiceRepository(session),
        contract_repository=SQLAlchemyOpenAPIContractRepository(session),
        registry_query=SQLAlchemyOpenAPIRegistryQuery(session),
    )


type GetAuthorizationManifestHandlerDep = Annotated[
    GetAuthorizationManifestHandler,
    Depends(provide_get_authorization_manifest_handler),
]

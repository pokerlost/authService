"""Master AUTO service-authentication dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from api.dependencies import ApplicationResourcesDep, DatabaseSession, SettingsDep
from application.service_authentication import (
    CreateServiceCredentialHandler,
    CreateServicePrincipalHandler,
    GrantServiceAudienceHandler,
    RevokeServiceAudienceHandler,
    RevokeServiceCredentialHandler,
)
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyPrincipalRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServiceCredentialRepository,
    SQLAlchemyServicePrincipalRepository,
)


def provide_create_service_principal_handler(
    session: DatabaseSession,
) -> CreateServicePrincipalHandler:
    """Compose the same AUTO principal handler used by the operator CLI."""
    return CreateServicePrincipalHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type CreateServicePrincipalHandlerDep = Annotated[
    CreateServicePrincipalHandler,
    Depends(provide_create_service_principal_handler),
]


def provide_create_service_credential_handler(
    session: DatabaseSession,
    resources: ApplicationResourcesDep,
    settings: SettingsDep,
) -> CreateServiceCredentialHandler:
    """Compose one-time service credential issuance without plaintext persistence."""
    return CreateServiceCredentialHandler(
        principal_repository=SQLAlchemyPrincipalRepository(session),
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        service_credential_repository=SQLAlchemyServiceCredentialRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
        protector=resources.service_credential_protector,
        credential_ttl=settings.service_auth.credential_ttl,
    )


type CreateServiceCredentialHandlerDep = Annotated[
    CreateServiceCredentialHandler,
    Depends(provide_create_service_credential_handler),
]


def provide_revoke_service_credential_handler(
    session: DatabaseSession,
) -> RevokeServiceCredentialHandler:
    """Compose idempotent known-credential revocation through the accepted handler."""
    return RevokeServiceCredentialHandler(
        SQLAlchemyServiceCredentialRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeServiceCredentialHandlerDep = Annotated[
    RevokeServiceCredentialHandler,
    Depends(provide_revoke_service_credential_handler),
]


def provide_grant_service_audience_handler(
    session: DatabaseSession,
) -> GrantServiceAudienceHandler:
    """Compose idempotent source-to-target audience grant creation."""
    return GrantServiceAudienceHandler(
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        grant_repository=SQLAlchemyServiceAudienceGrantRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type GrantServiceAudienceHandlerDep = Annotated[
    GrantServiceAudienceHandler,
    Depends(provide_grant_service_audience_handler),
]


def provide_revoke_service_audience_handler(
    session: DatabaseSession,
) -> RevokeServiceAudienceHandler:
    """Compose idempotent source-to-target audience grant revocation."""
    return RevokeServiceAudienceHandler(
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        grant_repository=SQLAlchemyServiceAudienceGrantRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeServiceAudienceHandlerDep = Annotated[
    RevokeServiceAudienceHandler,
    Depends(provide_revoke_service_audience_handler),
]

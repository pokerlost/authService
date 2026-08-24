"""Explicit OAuth2 scope grant dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from api.dependencies import DatabaseSession, SettingsDep
from application.scope_grants import (
    GrantRoleScopeHandler,
    GrantServiceScopeHandler,
    ListRoleScopesHandler,
    ListServiceScopesHandler,
    RevokeRoleScopeHandler,
    RevokeServiceScopeHandler,
)
from persistence.queries import SQLAlchemyScopeQuery
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyRoleScopeGrantRepository,
    SQLAlchemyServiceAudienceGrantRepository,
    SQLAlchemyServicePrincipalRepository,
    SQLAlchemyServiceScopeGrantRepository,
)


def provide_grant_role_scope_handler(session: DatabaseSession) -> GrantRoleScopeHandler:
    """Compose active-scope validation, direct grant persistence, and audit."""
    return GrantRoleScopeHandler(
        grant_repository=SQLAlchemyRoleScopeGrantRepository(session),
        scope_query=SQLAlchemyScopeQuery(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type GrantRoleScopeHandlerDep = Annotated[
    GrantRoleScopeHandler,
    Depends(provide_grant_role_scope_handler),
]


def provide_revoke_role_scope_handler(session: DatabaseSession) -> RevokeRoleScopeHandler:
    """Compose idempotent direct role scope revocation and audit."""
    return RevokeRoleScopeHandler(
        grant_repository=SQLAlchemyRoleScopeGrantRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeRoleScopeHandlerDep = Annotated[
    RevokeRoleScopeHandler,
    Depends(provide_revoke_role_scope_handler),
]


def provide_list_role_scopes_handler(
    session: DatabaseSession,
) -> ListRoleScopesHandler:
    """Compose bounded role grant inspection."""
    return ListRoleScopesHandler(SQLAlchemyRoleScopeGrantRepository(session))


type ListRoleScopesHandlerDep = Annotated[
    ListRoleScopesHandler,
    Depends(provide_list_role_scopes_handler),
]


def provide_grant_service_scope_handler(
    session: DatabaseSession,
) -> GrantServiceScopeHandler:
    """Compose target ownership, audience, exact scope grant, and audit."""
    return GrantServiceScopeHandler(
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        audience_repository=SQLAlchemyServiceAudienceGrantRepository(session),
        grant_repository=SQLAlchemyServiceScopeGrantRepository(session),
        scope_query=SQLAlchemyScopeQuery(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type GrantServiceScopeHandlerDep = Annotated[
    GrantServiceScopeHandler,
    Depends(provide_grant_service_scope_handler),
]


def provide_revoke_service_scope_handler(
    session: DatabaseSession,
) -> RevokeServiceScopeHandler:
    """Compose idempotent service scope revocation and audit."""
    return RevokeServiceScopeHandler(
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        grant_repository=SQLAlchemyServiceScopeGrantRepository(session),
        audit_repository=SQLAlchemyAuditEventRepository(session),
    )


type RevokeServiceScopeHandlerDep = Annotated[
    RevokeServiceScopeHandler,
    Depends(provide_revoke_service_scope_handler),
]


def provide_list_service_scopes_handler(
    session: DatabaseSession,
) -> ListServiceScopesHandler:
    """Compose bounded source-service and target-resource grant inspection."""
    return ListServiceScopesHandler(
        service_principal_repository=SQLAlchemyServicePrincipalRepository(session),
        grant_repository=SQLAlchemyServiceScopeGrantRepository(session),
    )


type ListServiceScopesHandlerDep = Annotated[
    ListServiceScopesHandler,
    Depends(provide_list_service_scopes_handler),
]


def get_scope_grant_list_limit(settings: SettingsDep) -> int:
    """Use the registry operation bound for control-plane grant materialization."""
    return settings.openapi_registry.max_operations


type ScopeGrantListLimitDep = Annotated[int, Depends(get_scope_grant_list_limit)]

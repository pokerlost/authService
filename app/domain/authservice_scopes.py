"""Canonical OAuth2 operation scopes owned by authService."""

from __future__ import annotations

from typing import Final

HUMAN_SESSION_SCOPE_IDS: Final = (
    "authService.account.changePassword",
    "authService.auth.logout",
    "authService.auth.logoutAll",
    "authService.sessions.list",
    "authService.sessions.revoke",
)

SUPPORT_SCOPE_IDS: Final = ("authService.support.getUserAccount",)

MASTER_SCOPE_IDS: Final = (
    "authService.master.activateOpenApiContract",
    "authService.master.createAutoPrincipal",
    "authService.master.createMasterAccount",
    "authService.master.createServiceCredential",
    "authService.master.createSupportAccount",
    "authService.master.diffOpenApiContract",
    "authService.master.disableAccount",
    "authService.master.enableAccount",
    "authService.master.getAuthorizationManifest",
    "authService.master.getOpenApiContract",
    "authService.master.getRegisteredService",
    "authService.master.grantRoleScope",
    "authService.master.grantServiceAudience",
    "authService.master.grantServiceScope",
    "authService.master.listAuditEvents",
    "authService.master.listOpenApiContracts",
    "authService.master.listRegisteredServices",
    "authService.master.listRoleScopes",
    "authService.master.listServiceScopes",
    "authService.master.registerOpenApiContract",
    "authService.master.resetHumanPassword",
    "authService.master.retireOpenApiContract",
    "authService.master.revokeRoleScope",
    "authService.master.revokeServiceAudience",
    "authService.master.revokeServiceCredential",
    "authService.master.revokeServiceScope",
    "authService.master.validateOpenApiContract",
)

AUTH_SERVICE_PROTECTED_SCOPE_IDS: Final = frozenset(
    (*HUMAN_SESSION_SCOPE_IDS, *SUPPORT_SCOPE_IDS, *MASTER_SCOPE_IDS)
)

AUTH_SERVICE_PUBLIC_OPERATION_IDS: Final = frozenset(
    {
        "authService.jwks.get",
        "authService.oauth.token",
        "authService.openapi.get",
        "authService.root",
        "authService.users.register",
    }
)

AUTH_SERVICE_OPERATION_IDS: Final = frozenset(
    (*AUTH_SERVICE_PUBLIC_OPERATION_IDS, *AUTH_SERVICE_PROTECTED_SCOPE_IDS)
)

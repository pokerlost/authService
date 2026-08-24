"""Explicit OAuth2 scope dependencies for master control-plane RPCs."""

from __future__ import annotations

from typing import Annotated

from fastapi import Security

from api.dependencies.authentication import authenticate_human_principal
from application.authentication import AuthenticatedHumanPrincipal

type ActivateOpenApiContractPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.activateOpenApiContract"],
    ),
]
type CreateAutoPrincipalPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.createAutoPrincipal"]),
]
type CreateMasterAccountPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.createMasterAccount"]),
]
type CreateServiceCredentialPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.createServiceCredential"],
    ),
]
type CreateSupportAccountPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.createSupportAccount"]),
]
type DiffOpenApiContractPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.diffOpenApiContract"]),
]
type DisableAccountPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.disableAccount"]),
]
type EnableAccountPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.enableAccount"]),
]
type GetAuthorizationManifestPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.getAuthorizationManifest"],
    ),
]
type GetOpenApiContractPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.getOpenApiContract"]),
]
type GetRegisteredServicePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.getRegisteredService"]),
]
type GrantRoleScopePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.grantRoleScope"]),
]
type GrantServiceAudiencePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.grantServiceAudience"]),
]
type GrantServiceScopePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.grantServiceScope"]),
]
type ListAuditEventsPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.listAuditEvents"]),
]
type ListOpenApiContractsPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.listOpenApiContracts"]),
]
type ListRegisteredServicesPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.listRegisteredServices"],
    ),
]
type ListRoleScopesPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.listRoleScopes"]),
]
type ListServiceScopesPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.listServiceScopes"]),
]
type RegisterOpenApiContractPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.registerOpenApiContract"],
    ),
]
type ResetHumanPasswordPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.resetHumanPassword"]),
]
type RetireOpenApiContractPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.retireOpenApiContract"]),
]
type RevokeRoleScopePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.revokeRoleScope"]),
]
type RevokeServiceAudiencePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.revokeServiceAudience"]),
]
type RevokeServiceCredentialPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.revokeServiceCredential"],
    ),
]
type RevokeServiceScopePrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(authenticate_human_principal, scopes=["authService.master.revokeServiceScope"]),
]
type ValidateOpenApiContractPrincipalDep = Annotated[
    AuthenticatedHumanPrincipal,
    Security(
        authenticate_human_principal,
        scopes=["authService.master.validateOpenApiContract"],
    ),
]

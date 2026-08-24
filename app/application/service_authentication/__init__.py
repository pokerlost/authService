"""AUTO service authentication application facade."""

from __future__ import annotations

from .create_service_credential import (
    CreatedServiceCredential,
    CreateServiceCredentialCommand,
    CreateServiceCredentialHandler,
)
from .create_service_principal import CreateServicePrincipalCommand, CreateServicePrincipalHandler
from .grant_service_audience import GrantServiceAudienceCommand, GrantServiceAudienceHandler
from .issue_service_token import (
    IssueServiceTokenCommand,
    IssueServiceTokenHandler,
    IssueServiceTokenResult,
)
from .revoke_service_audience import RevokeServiceAudienceCommand, RevokeServiceAudienceHandler
from .revoke_service_credential import (
    RevokeServiceCredentialCommand,
    RevokeServiceCredentialHandler,
)

__all__ = (
    "CreateServiceCredentialCommand",
    "CreateServiceCredentialHandler",
    "CreateServicePrincipalCommand",
    "CreateServicePrincipalHandler",
    "CreatedServiceCredential",
    "GrantServiceAudienceCommand",
    "GrantServiceAudienceHandler",
    "IssueServiceTokenCommand",
    "IssueServiceTokenHandler",
    "IssueServiceTokenResult",
    "RevokeServiceAudienceCommand",
    "RevokeServiceAudienceHandler",
    "RevokeServiceCredentialCommand",
    "RevokeServiceCredentialHandler",
)

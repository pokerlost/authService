"""AUTO service authentication failure facade."""

from __future__ import annotations

from .invalid_service_credentials import InvalidServiceCredentials
from .service_credential_not_found import ServiceCredentialNotFound
from .service_principal_already_exists import ServicePrincipalAlreadyExists
from .service_principal_not_found import ServicePrincipalNotFound

__all__ = (
    "InvalidServiceCredentials",
    "ServiceCredentialNotFound",
    "ServicePrincipalAlreadyExists",
    "ServicePrincipalNotFound",
)

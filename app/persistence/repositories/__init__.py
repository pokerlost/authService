"""Concrete SQLAlchemy repository facade."""

from __future__ import annotations

from .api_operation import SQLAlchemyAPIOperationRepository
from .audit_event import SQLAlchemyAuditEventRepository
from .base import SQLAlchemyEntityRepository, SQLAlchemyRepository
from .human_account import SQLAlchemyHumanAccountRepository
from .openapi_contract import SQLAlchemyOpenAPIContractRepository
from .operation_identity import SQLAlchemyOperationIdentityRepository
from .password_credential import SQLAlchemyPasswordCredentialRepository
from .principal import SQLAlchemyPrincipalRepository
from .refresh_token import SQLAlchemyRefreshTokenRepository
from .registered_service import SQLAlchemyRegisteredServiceRepository
from .role_scope_grant import SQLAlchemyRoleScopeGrantRepository
from .security_cleanup import SQLAlchemySecurityCleanupRepository
from .security_rate_limit import SQLAlchemySecurityRateLimitRepository
from .service_audience_grant import SQLAlchemyServiceAudienceGrantRepository
from .service_credential import SQLAlchemyServiceCredentialRepository
from .service_principal import SQLAlchemyServicePrincipalRepository
from .service_scope_grant import SQLAlchemyServiceScopeGrantRepository
from .session import SQLAlchemySessionRepository
from .session_scope import SQLAlchemySessionScopeRepository

__all__ = (
    "SQLAlchemyAPIOperationRepository",
    "SQLAlchemyAuditEventRepository",
    "SQLAlchemyEntityRepository",
    "SQLAlchemyHumanAccountRepository",
    "SQLAlchemyOpenAPIContractRepository",
    "SQLAlchemyOperationIdentityRepository",
    "SQLAlchemyPasswordCredentialRepository",
    "SQLAlchemyPrincipalRepository",
    "SQLAlchemyRefreshTokenRepository",
    "SQLAlchemyRegisteredServiceRepository",
    "SQLAlchemyRepository",
    "SQLAlchemyRoleScopeGrantRepository",
    "SQLAlchemySecurityCleanupRepository",
    "SQLAlchemySecurityRateLimitRepository",
    "SQLAlchemyServiceAudienceGrantRepository",
    "SQLAlchemyServiceCredentialRepository",
    "SQLAlchemyServicePrincipalRepository",
    "SQLAlchemyServiceScopeGrantRepository",
    "SQLAlchemySessionRepository",
    "SQLAlchemySessionScopeRepository",
)

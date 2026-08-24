"""Durable security audit event taxonomy."""

from __future__ import annotations

from enum import StrEnum


class AuditEventType(StrEnum):
    """Finite first-production security audit event types."""

    USER_REGISTERED = "user_registered"
    PASSWORD_GRANT_SUCCEEDED = "password_grant_succeeded"
    PASSWORD_GRANT_FAILED = "password_grant_failed"
    CLIENT_CREDENTIALS_SUCCEEDED = "client_credentials_succeeded"
    CLIENT_CREDENTIALS_FAILED = "client_credentials_failed"
    OAUTH_TOKEN_REFRESHED = "oauth_token_refreshed"
    OAUTH_REFRESH_REUSE_DETECTED = "oauth_refresh_reuse_detected"
    SESSION_REVOKED = "session_revoked"
    ALL_SESSIONS_REVOKED = "all_sessions_revoked"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_BY_MASTER = "password_reset_by_master"
    SUPPORT_ACCOUNT_CREATED = "support_account_created"
    MASTER_ACCOUNT_CREATED = "master_account_created"
    ACCOUNT_DISABLED = "account_disabled"
    ACCOUNT_ENABLED = "account_enabled"
    SERVICE_PRINCIPAL_CREATED = "service_principal_created"
    SERVICE_CREDENTIAL_CREATED = "service_credential_created"
    SERVICE_CREDENTIAL_REVOKED = "service_credential_revoked"
    SERVICE_AUDIENCE_GRANTED = "service_audience_granted"
    SERVICE_AUDIENCE_REVOKED = "service_audience_revoked"
    SERVICE_SCOPE_GRANTED = "service_scope_granted"
    SERVICE_SCOPE_REVOKED = "service_scope_revoked"
    ROLE_SCOPE_GRANTED = "role_scope_granted"
    ROLE_SCOPE_REVOKED = "role_scope_revoked"
    OPENAPI_CONTRACT_REGISTERED = "openapi_contract_registered"
    OPENAPI_CONTRACT_VALIDATED = "openapi_contract_validated"
    OPENAPI_CONTRACT_ACTIVATION_SUCCEEDED = "openapi_contract_activation_succeeded"
    OPENAPI_CONTRACT_ACTIVATION_FAILED = "openapi_contract_activation_failed"
    OPENAPI_CONTRACT_RETIRED = "openapi_contract_retired"

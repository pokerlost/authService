"""Security reason for explicit human session revocation."""

from __future__ import annotations

from enum import StrEnum


class SessionRevocationReason(StrEnum):
    """Current closed set of session-family revocation causes."""

    REFRESH_REUSE = "refresh_reuse"
    PRINCIPAL_DISABLED = "principal_disabled"
    INVALID_HUMAN_ROLE = "invalid_human_role"
    LOGOUT = "logout"
    LOGOUT_ALL = "logout_all"
    MANUAL = "manual"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    OAUTH2_MIGRATION = "oauth2_migration"

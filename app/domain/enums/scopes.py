"""authService access-token scope catalog."""

from __future__ import annotations

import re
from enum import StrEnum, unique
from typing import Final

_SCOPE_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+$")


@unique
class Scopes(StrEnum):
    """Stable capabilities owned by authService."""

    CLIENT_MANAGE = "auth.client.manage"
    INTERNAL_ISSUE_LOGIN_GRANT = "auth.internal.issueLoginGrant"
    INTERNAL_PROVISION_HUMAN = "auth.internal.provisionHuman"
    INTERNAL_REPLACE_PRINCIPAL_SCOPES = "auth.internal.replacePrincipalScopes"
    INTERNAL_SET_PRINCIPAL_STATUS = "auth.internal.setPrincipalStatus"
    PRINCIPAL_REPLACE_SCOPES = "auth.principal.replaceScopes"
    SCOPE_MANAGE = "auth.scope.manage"

    def __new__(cls, value: str) -> Scopes:
        """Reject values outside the stable dotted lowerCamelCase contract."""
        if _SCOPE_PATTERN.fullmatch(value) is None:
            raise ValueError("Pokerlost scopes must contain dotted lowerCamelCase segments")
        member = str.__new__(cls, value)
        member._value_ = value
        return member


_SCOPE_DESCRIPTIONS: Final[dict[Scopes, str]] = {
    Scopes.CLIENT_MANAGE: "Manage authorization clients.",
    Scopes.INTERNAL_ISSUE_LOGIN_GRANT: "Issue a one-time human login grant.",
    Scopes.INTERNAL_PROVISION_HUMAN: "Provision a human authorization principal.",
    Scopes.INTERNAL_REPLACE_PRINCIPAL_SCOPES: (
        "Replace a principal's exact scopes from an internal service."
    ),
    Scopes.INTERNAL_SET_PRINCIPAL_STATUS: "Set an authorization principal's status.",
    Scopes.PRINCIPAL_REPLACE_SCOPES: "Replace a principal's exact scopes.",
    Scopes.SCOPE_MANAGE: "Manage the authorization scope catalog.",
}


def scope_descriptions() -> dict[str, str]:
    """Return the standard OAuth2 scope catalog for OpenAPI."""
    if frozenset(_SCOPE_DESCRIPTIONS) != frozenset(Scopes):
        raise RuntimeError("Every local Pokerlost scope must have exactly one description")
    if any(not description.strip() for description in _SCOPE_DESCRIPTIONS.values()):
        raise RuntimeError("Pokerlost scope descriptions must not be empty")
    return {scope.value: _SCOPE_DESCRIPTIONS[scope] for scope in Scopes}

"""Human login result."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from domain.enums import Role


@dataclass(frozen=True, slots=True)
class LoginResult:
    """Newly issued OAuth2 human session credentials and negotiated scopes."""

    principal_id: UUID
    role: Role
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    scopes: frozenset[str]

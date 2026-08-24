"""Issue short-lived human access JWTs with scope permissions and role classification."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final
from uuid import UUID, uuid4

import jwt

from domain.enums import Role

from .oauth_scope_parser import OAuthScopeParser
from .signing_key_provider import SigningKeyProvider

_ALGORITHM: Final = "RS256"
_TOKEN_USE: Final = "access"


class AccessTokenIssuer:
    """Issue RS256 human access tokens with required claims and kid."""

    __slots__ = (
        "_audience",
        "_issuer",
        "_max_access_token_bytes",
        "_scope_parser",
        "_signing_key_provider",
        "_ttl_seconds",
    )

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        ttl_seconds: int,
        signing_key_provider: SigningKeyProvider,
        scope_parser: OAuthScopeParser,
        max_access_token_bytes: int,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._ttl_seconds = ttl_seconds
        self._signing_key_provider = signing_key_provider
        self._scope_parser = scope_parser
        self._max_access_token_bytes = max_access_token_bytes

    def issue_human_access_token(
        self,
        principal_id: UUID,
        session_id: UUID,
        role: Role,
        scopes: frozenset[str],
    ) -> str:
        """Emit one short-lived human access JWT."""
        if role is Role.AUTO:
            raise ValueError("Role.AUTO is not allowed for human access tokens")
        if role not in (Role.USER, Role.SUPPORT, Role.MASTER):
            raise ValueError("Unknown or unsupported role for human access token")

        issued_at = datetime.now(UTC).replace(microsecond=0)
        timestamp = int(issued_at.timestamp())
        claims = {
            "iss": self._issuer,
            "sub": str(principal_id),
            "aud": self._audience,
            "iat": timestamp,
            "nbf": timestamp,
            "exp": timestamp + self._ttl_seconds,
            "jti": str(uuid4()),
            "token_use": _TOKEN_USE,
            "role": role.value,
            "sid": str(session_id),
            "scope": self._scope_parser.serialize(scopes),
        }

        token = jwt.encode(
            payload=claims,
            key=self._signing_key_provider.active_private_key,
            algorithm=_ALGORITHM,
            headers={
                "kid": self._signing_key_provider.active_kid,
                "typ": "at+jwt",
                "alg": _ALGORITHM,
            },
        )
        if len(token.encode("ascii")) > self._max_access_token_bytes:
            raise ValueError("Access token exceeds the configured byte limit")
        return token

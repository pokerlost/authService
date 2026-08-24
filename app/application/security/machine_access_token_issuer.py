"""Issue short-lived AUTO access JWTs with service isolation claims."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Final
from uuid import UUID, uuid4

import jwt

from domain.types import ServiceSlug

from .oauth_scope_parser import OAuthScopeParser
from .signing_key_provider import SigningKeyProvider

_ALGORITHM: Final = "RS256"
_TOKEN_USE: Final = "access"


class MachineAccessTokenIssuer:
    """Issue RS256 machine tokens without human session claims."""

    __slots__ = (
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
        ttl_seconds: int,
        signing_key_provider: SigningKeyProvider,
        scope_parser: OAuthScopeParser,
        max_access_token_bytes: int,
    ) -> None:
        self._issuer = issuer
        self._ttl_seconds = ttl_seconds
        self._signing_key_provider = signing_key_provider
        self._scope_parser = scope_parser
        self._max_access_token_bytes = max_access_token_bytes

    def issue_machine_access_token(
        self,
        *,
        principal_id: UUID,
        service: ServiceSlug,
        audience: ServiceSlug,
        scopes: frozenset[str],
    ) -> str:
        """Emit one audience-bound AUTO access JWT without a session ID."""
        issued_at = datetime.now(UTC).replace(microsecond=0)
        timestamp = int(issued_at.timestamp())
        claims = {
            "iss": self._issuer,
            "sub": str(principal_id),
            "aud": audience,
            "iat": timestamp,
            "nbf": timestamp,
            "exp": timestamp + self._ttl_seconds,
            "jti": str(uuid4()),
            "token_use": _TOKEN_USE,
            "role": "auto",
            "service": service,
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

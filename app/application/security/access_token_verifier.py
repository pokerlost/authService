"""Strict cryptographic and protocol verification for access JWTs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Final
from uuid import UUID

import jwt
from jwt.exceptions import PyJWTError
from pydantic import SecretStr

from application.errors import InvalidAccessToken
from domain.enums import Role

from .access_token_claims import AccessTokenClaims
from .oauth_scope_parser import OAuthScopeParser
from .signing_key_provider import SigningKeyProvider

_ALGORITHM: Final = "RS256"
_TOKEN_TYPE: Final = "at+jwt"
_TOKEN_USE: Final = "access"
_REQUIRED_CLAIMS: Final = (
    "iss",
    "sub",
    "aud",
    "iat",
    "nbf",
    "exp",
    "jti",
    "token_use",
    "role",
    "sid",
    "scope",
)


class AccessTokenVerifier:
    """Verify one RS256 access JWT without persistence or transport concerns."""

    __slots__ = (
        "_audience",
        "_issuer",
        "_leeway",
        "_scope_parser",
        "_signing_key_provider",
    )

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        leeway: timedelta,
        signing_key_provider: SigningKeyProvider,
        scope_parser: OAuthScopeParser,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._leeway = leeway
        self._signing_key_provider = signing_key_provider
        self._scope_parser = scope_parser

    def verify(self, token: SecretStr) -> AccessTokenClaims:
        """Return normalized claims or one generic application authentication error."""
        try:
            raw_token = token.get_secret_value()
            header = jwt.get_unverified_header(raw_token)
            if header.get("alg") != _ALGORITHM or header.get("typ") != _TOKEN_TYPE:
                raise ValueError

            kid = header.get("kid")
            if not isinstance(kid, str) or not kid:
                raise ValueError
            public_key = self._signing_key_provider.get_public_key(kid)
            if public_key is None:
                raise ValueError

            payload = jwt.decode(
                jwt=raw_token,
                key=public_key,
                algorithms=[_ALGORITHM],
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._leeway,
                options={
                    "require": list(_REQUIRED_CLAIMS),
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_sub": True,
                    "verify_jti": True,
                    "strict_aud": True,
                },
            )
            if payload["iss"] != self._issuer or payload["aud"] != self._audience:
                raise ValueError
            if payload["token_use"] != _TOKEN_USE:
                raise ValueError

            issued_at = self._parse_timestamp(payload["iat"])
            not_before = self._parse_timestamp(payload["nbf"])
            expires_at = self._parse_timestamp(payload["exp"])
            if issued_at > expires_at or not_before > expires_at:
                raise ValueError

            role_value = payload["role"]
            if not isinstance(role_value, str):
                raise ValueError
            return AccessTokenClaims(
                principal_id=self._parse_uuid(payload["sub"]),
                session_id=self._parse_uuid(payload["sid"]),
                role=Role(role_value),
                token_id=self._parse_uuid(payload["jti"]),
                issued_at=issued_at,
                expires_at=expires_at,
                scopes=self._scope_parser.parse_claim(payload["scope"]),
            )
        except (KeyError, OverflowError, PyJWTError, TypeError, ValueError):
            raise InvalidAccessToken from None

    @staticmethod
    def _parse_uuid(value: object) -> UUID:
        """Parse one required string UUID claim."""
        if not isinstance(value, str):
            raise ValueError
        return UUID(value)

    @staticmethod
    def _parse_timestamp(value: object) -> datetime:
        """Parse one integer JWT NumericDate as an aware UTC datetime."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError
        return datetime.fromtimestamp(value, UTC)

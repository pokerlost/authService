"""Generate and protect opaque refresh credentials."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass, field
from typing import Final

from pydantic import SecretStr

_VERSION: Final = "rt1"
_LOOKUP_BYTES: Final = 16
_SECRET_BYTES: Final = 32
_LOOKUP_LENGTH: Final = 22
_SECRET_LENGTH: Final = 43
_MAX_TOKEN_LENGTH: Final = 128
_BASE64URL_PATTERN: Final = re.compile(r"[A-Za-z0-9_-]+\Z")


@dataclass(frozen=True, slots=True)
class IssuedRefreshToken:
    """Client token plus its non-plaintext database representation."""

    token: str = field(repr=False)
    lookup_id: str
    secret_digest: bytes = field(repr=False)


@dataclass(frozen=True, slots=True)
class ParsedRefreshToken:
    """Strictly parsed refresh-token locator and private secret."""

    lookup_id: str
    secret: str = field(repr=False)


class RefreshTokenProtector:
    """Protect opaque refresh secrets with HMAC-SHA-256 and a server pepper."""

    __slots__ = ("_pepper",)

    def __init__(self, pepper: SecretStr) -> None:
        self._pepper = pepper.get_secret_value().encode()

    def generate(self) -> IssuedRefreshToken:
        """Generate one versioned opaque token and its 32-byte digest."""
        lookup_id = secrets.token_urlsafe(_LOOKUP_BYTES)
        secret = secrets.token_urlsafe(_SECRET_BYTES)
        token = f"{_VERSION}.{lookup_id}.{secret}"
        return IssuedRefreshToken(
            token=token,
            lookup_id=lookup_id,
            secret_digest=self.compute_digest(lookup_id=lookup_id, secret=secret),
        )

    def parse(self, token: SecretStr) -> ParsedRefreshToken | None:
        """Parse only the exact supported refresh-token format."""
        raw_token = token.get_secret_value()
        if not raw_token or len(raw_token) > _MAX_TOKEN_LENGTH:
            return None
        parts = raw_token.split(".")
        if len(parts) != 3:
            return None
        version, lookup_id, secret = parts
        if version != _VERSION:
            return None
        if len(lookup_id) != _LOOKUP_LENGTH or len(secret) != _SECRET_LENGTH:
            return None
        if (
            _BASE64URL_PATTERN.fullmatch(lookup_id) is None
            or _BASE64URL_PATTERN.fullmatch(secret) is None
        ):
            return None
        return ParsedRefreshToken(lookup_id=lookup_id, secret=secret)

    def compute_digest(self, *, lookup_id: str, secret: str) -> bytes:
        """Compute the canonical locator-and-secret HMAC digest."""
        message = f"{lookup_id}.{secret}".encode()
        return hmac.new(self._pepper, message, hashlib.sha256).digest()

    def verify_digest(self, parsed: ParsedRefreshToken, expected_digest: bytes) -> bool:
        """Compare a supplied credential with a stored digest in constant time."""
        candidate_digest = self.compute_digest(
            lookup_id=parsed.lookup_id,
            secret=parsed.secret,
        )
        return hmac.compare_digest(candidate_digest, expected_digest)

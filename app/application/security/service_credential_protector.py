"""Generate and protect AUTO service credentials."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from typing import Final

from pydantic import SecretStr

_CLIENT_ID_BYTES: Final = 18
_CLIENT_SECRET_BYTES: Final = 32


@dataclass(frozen=True, slots=True)
class IssuedServiceCredential:
    """One-time client credential plus its digest-only persistence value."""

    client_id: str
    client_secret: SecretStr = field(repr=False)
    secret_digest: bytes = field(repr=False)


class ServiceCredentialProtector:
    """Protect service credentials with dedicated HMAC-SHA-256 keying material."""

    __slots__ = ("_dummy_digest", "_pepper")

    def __init__(self, pepper: SecretStr) -> None:
        self._pepper = pepper.get_secret_value().encode()
        self._dummy_digest = self.compute_digest(
            client_id="invalid-client-id",
            client_secret=SecretStr("invalid-client-secret"),
        )

    def generate(self) -> IssuedServiceCredential:
        """Generate a random public client ID and a 256-bit private secret."""
        client_id = secrets.token_urlsafe(_CLIENT_ID_BYTES)
        client_secret = SecretStr(secrets.token_urlsafe(_CLIENT_SECRET_BYTES))
        return IssuedServiceCredential(
            client_id=client_id,
            client_secret=client_secret,
            secret_digest=self.compute_digest(
                client_id=client_id,
                client_secret=client_secret,
            ),
        )

    def compute_digest(self, *, client_id: str, client_secret: SecretStr) -> bytes:
        """Compute HMAC over canonical ``<client_id>.<client_secret>`` bytes."""
        message = f"{client_id}.{client_secret.get_secret_value()}".encode()
        return hmac.new(self._pepper, message, hashlib.sha256).digest()

    def verify(
        self,
        *,
        client_id: str,
        client_secret: SecretStr,
        expected_digest: bytes | None,
    ) -> bool:
        """Compare a supplied credential with a stored or dummy digest in constant time."""
        candidate_digest = self.compute_digest(
            client_id=client_id,
            client_secret=client_secret,
        )
        return hmac.compare_digest(
            candidate_digest,
            expected_digest if expected_digest is not None else self._dummy_digest,
        )

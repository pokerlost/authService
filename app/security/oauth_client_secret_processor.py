"""Domain-separated OAuth2 client secret processing."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import re
import secrets

from pydantic import SecretStr

from application.ports import GeneratedOAuthClientSecret, OAuthClientSecretProcessor

_DOMAIN_SEPARATOR = b"pokerlost.oauth-client-secret.v1\x00"
_SECRET_BYTE_LENGTH = 32
_SECRET_TEXT_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")


class SHA256OAuthClientSecretProcessor(OAuthClientSecretProcessor):
    """Generate and verify canonical secrets using a dedicated SHA-256 domain."""

    def generate(self) -> GeneratedOAuthClientSecret:
        """Generate exactly 32 random bytes and return one unpadded URL-safe secret."""
        random_secret = secrets.token_bytes(_SECRET_BYTE_LENGTH)
        encoded_secret = base64.urlsafe_b64encode(random_secret).rstrip(b"=").decode("ascii")
        secret = SecretStr(encoded_secret)
        return GeneratedOAuthClientSecret(
            secret=secret,
            digest=self._digest(secret),
        )

    def verify(self, secret: SecretStr, expected_digest: bytes) -> bool:
        """Compare the dedicated digest in constant time without exposing the secret."""
        try:
            candidate_digest = self._digest(secret)
        except ValueError:
            candidate_digest = hashlib.sha256(_DOMAIN_SEPARATOR).digest()
        return hmac.compare_digest(candidate_digest, expected_digest)

    @staticmethod
    def _digest(secret: SecretStr) -> bytes:
        secret_text = secret.get_secret_value()
        if _SECRET_TEXT_PATTERN.fullmatch(secret_text) is None:
            raise ValueError("OAuth2 client secret has an invalid generated format")
        try:
            decoded_secret = base64.b64decode(
                f"{secret_text}=",
                altchars=b"-_",
                validate=True,
            )
        except binascii.Error, ValueError:
            raise ValueError("OAuth2 client secret has an invalid generated format") from None
        canonical_secret = base64.urlsafe_b64encode(decoded_secret).rstrip(b"=").decode("ascii")
        if len(decoded_secret) != _SECRET_BYTE_LENGTH or canonical_secret != secret_text:
            raise ValueError("OAuth2 client secret has an invalid generated format")
        return hashlib.sha256(_DOMAIN_SEPARATOR + secret_text.encode("ascii")).digest()

"""PyJWT-backed RS256 service access-token signer."""

from __future__ import annotations

import jwt
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pypokerlost.contracts.authorization import AccessTokenClaims

from application.ports import ServiceAccessTokenSigner
from configuration import JWTSettings

_ALGORITHM = "RS256"
_MINIMUM_RSA_KEY_SIZE = 2048


class PyJWTServiceAccessTokenSigner(ServiceAccessTokenSigner):
    """Load one RSA private key at composition and sign exact service claims."""

    __slots__ = ("_key", "_key_id")

    def __init__(self, settings: JWTSettings) -> None:
        """Load and validate one mounted RSA private key without retaining PEM bytes."""
        try:
            private_key_pem = settings.private_key_path.read_bytes()
        except OSError:
            raise ValueError("JWT private key could not be read") from None

        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None,
            )
        except TypeError, ValueError, UnsupportedAlgorithm:
            raise ValueError("JWT private key is not a valid unencrypted PEM key") from None
        finally:
            del private_key_pem

        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise ValueError("JWT private key must be an RSA private key")
        if private_key.key_size < _MINIMUM_RSA_KEY_SIZE:
            raise ValueError("JWT RSA private key must contain at least 2048 bits")

        self._key = private_key
        self._key_id = settings.key_id

    def sign(self, claims: AccessTokenClaims) -> str:
        """Return an RS256 compact JWT containing only the approved service claims."""
        payload = claims.model_dump(mode="json", by_alias=True, exclude_none=True)
        return jwt.encode(
            payload,
            self._key,
            algorithm=_ALGORITHM,
            headers={"kid": self._key_id, "typ": "JWT"},
        )

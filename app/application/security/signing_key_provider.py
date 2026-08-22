"""Filesystem-backed asymmetric RSA signing key provider."""

from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Final

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    load_pem_private_key,
    load_pem_public_key,
)

from configuration import JWTSettings

_KEY_FILE_SUFFIX: Final = ".pem"
_KID_PATTERN: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{3,63}$")
_MIN_RSA_BITS: Final = 2048


class SigningKeyProvider:
    """Load and validate signing keys from mounted PEM files."""

    __slots__ = ("_active_kid", "_jwks_payload", "_private_key")

    def __init__(self, settings: JWTSettings) -> None:
        active_private_key_path = Path(settings.active_private_key_path)
        active_private_key = self._load_private_key(active_private_key_path)
        retained_public_keys = self._load_public_keys(Path(settings.retained_public_key_directory))
        active_public_key = active_private_key.public_key()
        self._validate_rsa_minimum_bits(active_public_key)

        self._active_kid = settings.active_kid
        self._private_key = active_private_key

        if self._active_kid in retained_public_keys:
            retained_public_key = retained_public_keys[self._active_kid]
            if not self._keys_equal(active_public_key, retained_public_key):
                raise ValueError("Active private key does not match retained key for active kid")
            self._remove_public_key(retained_public_keys, self._active_kid)

        retained_public_keys_with_active = self._serialize_public_keys(retained_public_keys)
        active_jwk = self._serialize_key(self._active_kid, active_public_key)
        self._jwks_payload = [active_jwk, *retained_public_keys_with_active]

    @property
    def active_private_key(self) -> rsa.RSAPrivateKey:
        """Return the active RSA private key for signing."""
        return self._private_key

    @property
    def active_kid(self) -> str:
        """Return the configured active key identifier."""
        return self._active_kid

    def get_jwks_payload(self) -> dict[str, list[dict[str, str]]]:
        """Return public JWKS payload without private material."""
        return {"keys": self._jwks_payload}

    @staticmethod
    def _remove_public_key(entries: dict[str, rsa.RSAPublicKey], kid: str) -> None:
        """Remove one retained public entry that is represented by the active key."""
        del entries[kid]

    @staticmethod
    def _load_private_key(path: Path) -> rsa.RSAPrivateKey:
        """Load and validate an RSA private key from a PEM file."""
        if not path.exists() or not path.is_file():
            raise ValueError("Active private key file does not exist")

        key_data = path.read_bytes()
        if not key_data:
            raise ValueError("Active private key file is empty")

        try:
            key = load_pem_private_key(key_data, password=None)
        except (ValueError, TypeError) as exc:
            raise ValueError("Active private key is not a valid PEM private key") from exc

        if not isinstance(key, rsa.RSAPrivateKey):
            raise ValueError("Active private key must be RSA")

        SigningKeyProvider._validate_rsa_private_key(key)
        return key

    @staticmethod
    def _load_public_keys(path: Path) -> dict[str, rsa.RSAPublicKey]:
        """Load all RSA public keys from a directory using file-stem as kid."""
        if not path.exists() or not path.is_dir():
            raise ValueError("Retained public key directory does not exist")

        result: dict[str, rsa.RSAPublicKey] = {}
        for file_path in sorted(path.iterdir()):
            if not file_path.is_file() or file_path.suffix.lower() != _KEY_FILE_SUFFIX:
                continue

            kid = file_path.stem
            if _KID_PATTERN.fullmatch(kid) is None:
                raise ValueError("Retained public key filename stem is not a valid kid")
            if kid in result:
                raise ValueError("Duplicate retained key id")

            key_bytes = file_path.read_bytes()
            try:
                key = load_pem_public_key(key_bytes)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Retained key '{kid}' is not a valid PEM public key") from exc

            if not isinstance(key, rsa.RSAPublicKey):
                raise ValueError(f"Retained key '{kid}' is not RSA")

            SigningKeyProvider._validate_rsa_minimum_bits(key)
            result[kid] = key

        return result

    @staticmethod
    def _serialize_public_keys(
        retained_keys: dict[str, rsa.RSAPublicKey],
    ) -> list[dict[str, str]]:
        """Convert retained public keys to deterministic JWKS order."""
        return [
            SigningKeyProvider._serialize_key(kid, public_key)
            for kid, public_key in sorted(retained_keys.items())
        ]

    @staticmethod
    def _serialize_key(kid: str, key: rsa.RSAPublicKey) -> dict[str, str]:
        """Return one minimal RSA JWK entry."""
        numbers = key.public_numbers()
        return {
            "kty": "RSA",
            "kid": kid,
            "use": "sig",
            "alg": "RS256",
            "n": SigningKeyProvider._base64url_uint(numbers.n),
            "e": SigningKeyProvider._base64url_uint(numbers.e),
        }

    @staticmethod
    def _base64url_uint(value: int) -> str:
        """Encode an RSA integer using URL-safe base64 without padding."""
        length = (value.bit_length() + 7) // 8
        raw = value.to_bytes(length, byteorder="big")
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @staticmethod
    def _validate_rsa_private_key(key: rsa.RSAPrivateKey) -> None:
        """Reject non-compliant private RSA keys."""
        try:
            SigningKeyProvider._validate_rsa_minimum_bits(key.public_key())
            # Confirm that the parsed key can be encoded as RSA private PEM.
            key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption(),
            )
        except ValueError as exc:
            raise ValueError("Active private key is not valid for signing") from exc

    @staticmethod
    def _validate_rsa_minimum_bits(key: rsa.RSAPublicKey) -> None:
        """Ensure minimum RSA key size for production signing material."""
        if key.key_size < _MIN_RSA_BITS:
            raise ValueError("RSA key size is below minimum security level")

    @staticmethod
    def _keys_equal(left: rsa.RSAPublicKey, right: rsa.RSAPublicKey) -> bool:
        """Check RSA key equivalence by modulus and exponent."""
        left_numbers = left.public_numbers()
        right_numbers = right.public_numbers()
        return left_numbers.e == right_numbers.e and left_numbers.n == right_numbers.n

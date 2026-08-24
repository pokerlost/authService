"""Argon2id password hashing component."""

from __future__ import annotations

import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.low_level import Type
from pydantic import SecretStr


class Argon2PasswordHasher:
    """Hash and verify passwords using configured Argon2id parameters."""

    __slots__ = ("_dummy_hash", "_hasher")

    def __init__(
        self,
        *,
        time_cost: int,
        memory_cost_kib: int,
        parallelism: int,
        hash_length: int,
        salt_length: int,
    ) -> None:
        self._hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost_kib,
            parallelism=parallelism,
            hash_len=hash_length,
            salt_len=salt_length,
            type=Type.ID,
        )
        self._dummy_hash = self._hasher.hash(secrets.token_urlsafe(32))

    def hash(self, password: SecretStr) -> str:
        """Create a standard encoded Argon2id password hash."""
        return self._hasher.hash(password.get_secret_value())

    def verify(self, password: SecretStr, password_hash: str) -> bool:
        """Verify a password without exposing mismatch details."""
        try:
            return self._hasher.verify(password_hash, password.get_secret_value())
        except (InvalidHashError, VerificationError):
            return False

    def verify_or_dummy(self, password: SecretStr, password_hash: str | None) -> bool:
        """Perform Argon2 work even when no stored credential exists."""
        verified = self.verify(password, password_hash or self._dummy_hash)
        return password_hash is not None and verified

    def needs_rehash(self, password_hash: str) -> bool:
        """Report whether an encoded hash differs from configured parameters."""
        return self._hasher.check_needs_rehash(password_hash)

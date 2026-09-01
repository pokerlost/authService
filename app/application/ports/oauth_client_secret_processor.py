"""OAuth2 client secret generation and verification port."""

from __future__ import annotations

import re
from typing import ClassVar, Protocol

from pydantic import Field, SecretStr, field_validator
from pydantic_core import PydanticCustomError

from domain.oauth_client_credential import OAuthClientSecretDigest
from domain.value_model import ValueModel


class GeneratedOAuthClientSecret(ValueModel):
    """One-time raw OAuth2 client secret paired with its persistent digest."""

    pattern: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_-]{43}$")

    secret: SecretStr = Field(repr=False)
    digest: OAuthClientSecretDigest = Field(repr=False)

    @field_validator("secret")
    @classmethod
    def validate_secret(cls, secret: SecretStr) -> SecretStr:
        """Require the exact unpadded text shape produced from 32 random bytes."""
        if cls.pattern.fullmatch(secret.get_secret_value()) is None:
            raise PydanticCustomError(
                "invalid_oauth_client_secret",
                "OAuth2 client secret has an invalid generated format",
            )
        return secret


class OAuthClientSecretProcessor(Protocol):
    """Generate digest-only credentials and verify presented secrets."""

    def generate(self) -> GeneratedOAuthClientSecret:
        """Generate one raw secret and its dedicated persistent digest."""
        ...

    def verify(self, secret: SecretStr, expected_digest: bytes) -> bool:
        """Compare a presented secret with one persisted digest."""
        ...

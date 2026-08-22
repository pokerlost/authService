"""JWKS response schema."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from api.schemas.base import ResponseModel


class JwkSchema(ResponseModel):
    """Minimal RSA JWK shape used in JWKS payloads."""

    kty: Literal["RSA"] = Field(description="JSON Web Key type.")
    kid: str = Field(min_length=4, max_length=64, description="Deterministic key identifier.")
    use: Literal["sig"] = Field(description="Key usage.")
    alg: Literal["RS256"] = Field(description="Signing algorithm.")
    n: str = Field(description="RSA modulus encoded as URL-safe Base64 integer.")
    e: str = Field(description="RSA public exponent encoded as URL-safe Base64 integer.")


class JwksSchema(ResponseModel):
    """Standard JWKS response payload."""

    keys: list[JwkSchema]

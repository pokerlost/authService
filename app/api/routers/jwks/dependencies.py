"""JWKS dependency composition."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from api.dependencies import ApplicationResourcesDep
from application.security import SigningKeyProvider


def provide_signing_key_provider(
    resources: ApplicationResourcesDep,
) -> SigningKeyProvider:
    """Return the lifespan-owned signing key provider."""
    return resources.signing_key_provider


type SigningKeyProviderDep = Annotated[
    SigningKeyProvider,
    Depends(provide_signing_key_provider),
]

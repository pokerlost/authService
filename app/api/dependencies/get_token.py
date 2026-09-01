"""Focused getToken handler dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from application.oauth2.issue_client_credentials_token import (
    IssueClientCredentialsTokenHandler,
)
from persistence.queries import SQLAlchemyClientCredentialsQuery
from security import SHA256OAuthClientSecretProcessor

from .database import DatabaseSession
from .resources import ServiceAccessTokenSignerDep
from .settings import SettingsDep


def _resolve_issue_client_credentials_token_handler(
    session: DatabaseSession,
    signer: ServiceAccessTokenSignerDep,
    settings: SettingsDep,
) -> IssueClientCredentialsTokenHandler:
    """Compose one request-scoped issuance handler over the request transaction."""
    return IssueClientCredentialsTokenHandler(
        SQLAlchemyClientCredentialsQuery(session),
        SHA256OAuthClientSecretProcessor(),
        signer,
        issuer=settings.token.issuer,
        access_token_ttl_seconds=settings.token.access_token_ttl_seconds,
    )


type IssueClientCredentialsTokenHandlerDep = Annotated[
    IssueClientCredentialsTokenHandler,
    Depends(_resolve_issue_client_credentials_token_handler),
]

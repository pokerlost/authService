"""Focused OAuth2 token protocol and handler dependencies."""

from __future__ import annotations

from typing import Annotated, Final
from uuid import UUID

from fastapi import Depends, Form, Request, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import SecretStr, ValidationError

from api.schemas.requests import OAuthTokenRequest
from application.oauth2 import OAuth2ErrorCode, OAuth2TokenError
from application.oauth2.issue_client_credentials_token import (
    IssueClientCredentialsTokenHandler,
)
from domain.resource_indicator import ResourceIndicator
from domain.scope_name import ScopeName
from domain.value_model import ValueModel
from persistence.queries import SQLAlchemyClientCredentialsQuery
from security import SHA256OAuthClientSecretProcessor

from .database import DatabaseSession
from .resources import ServiceAccessTokenSignerDep
from .settings import SettingsDep

_TOKEN_FORM_MEDIA_TYPE: Final = "application/x-www-form-urlencoded"
_TOKEN_FORM_FIELDS: Final = frozenset({"grant_type", "scope", "resource"})
_CLIENT_CREDENTIALS_GRANT: Final = "client_credentials"
_http_basic = HTTPBasic(
    auto_error=False,
    scheme_name="OAuth2ClientBasic",
    description="Confidential OAuth2 client credentials.",
)


class _OAuthClientAuthentication(ValueModel):
    """Validated HTTP Basic client credentials with a protected secret value."""

    client_id: UUID
    client_secret: SecretStr


class _ParsedOAuthTokenInput(ValueModel):
    """Exact protocol values derived through Starlette form parsing."""

    requested_scopes: tuple[ScopeName, ...]
    resource: ResourceIndicator


async def _resolve_oauth_client_authentication(
    credentials: Annotated[HTTPBasicCredentials | None, Security(_http_basic)],
) -> _OAuthClientAuthentication:
    """Normalize every missing or malformed Basic credential to invalid_client."""
    if credentials is None or not credentials.password:
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_CLIENT)
    try:
        client_id = UUID(credentials.username)
    except ValueError:
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_CLIENT) from None
    if str(client_id) != credentials.username:
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_CLIENT)
    return _OAuthClientAuthentication(
        client_id=client_id,
        client_secret=SecretStr(credentials.password),
    )


type OAuthClientAuthentication = Annotated[
    _OAuthClientAuthentication,
    Depends(_resolve_oauth_client_authentication),
]


def _resolve_oauth_token_protocol_input(
    request: Request,
    form: Annotated[OAuthTokenRequest, Form()],
) -> _ParsedOAuthTokenInput:
    """Enforce exact form multiplicity and parse OAuth2 protocol values safely."""
    content_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
    if content_type != _TOKEN_FORM_MEDIA_TYPE:
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_REQUEST)
    if any(len(getattr(form, name)) != 1 for name in _TOKEN_FORM_FIELDS):
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_REQUEST)
    if form.grant_type[0] != _CLIENT_CREDENTIALS_GRANT:
        raise OAuth2TokenError(OAuth2ErrorCode.UNSUPPORTED_GRANT_TYPE)

    raw_scope = form.scope[0]
    raw_scope_tokens = raw_scope.split(" ")
    if not raw_scope or any(not token for token in raw_scope_tokens):
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_SCOPE)
    try:
        requested_scopes = tuple(ScopeName.parse(token) for token in raw_scope_tokens)
    except ValidationError:
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_SCOPE) from None
    if len(frozenset(requested_scopes)) != len(requested_scopes):
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_SCOPE)

    try:
        resource = ResourceIndicator.parse(form.resource[0])
    except ValidationError:
        raise OAuth2TokenError(OAuth2ErrorCode.INVALID_TARGET) from None
    return _ParsedOAuthTokenInput(
        requested_scopes=requested_scopes,
        resource=resource,
    )


type OAuthTokenProtocolInput = Annotated[
    _ParsedOAuthTokenInput,
    Depends(_resolve_oauth_token_protocol_input),
]


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
        issuer=settings.oauth2.issuer,
        access_token_ttl_seconds=settings.oauth2.access_token_ttl_seconds,
    )


type IssueClientCredentialsTokenHandlerDep = Annotated[
    IssueClientCredentialsTokenHandler,
    Depends(_resolve_issue_client_credentials_token_handler),
]

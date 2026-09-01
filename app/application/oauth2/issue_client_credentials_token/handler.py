"""Service-client credential token issuance orchestration."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from pydantic import SecretStr
from pypokerlost.types import (
    AuthorizationRole,
    PokerlostAccessTokenClaims,
    PrincipalStatus,
    PrincipalType,
    format_pokerlost_scope_string,
)

from application.oauth2 import GetTokenError, GetTokenErrorCode
from application.ports import (
    ClientCredentialsAuthorizationContext,
    ClientCredentialsQuery,
    Handler,
    OAuthClientSecretProcessor,
    ServiceAccessTokenSigner,
)
from domain.enums import (
    OAuthClientStatus,
    OAuthClientType,
    OAuthGrantType,
)

from .command import IssueClientCredentialsTokenCommand
from .result import IssueClientCredentialsTokenResult


class IssueClientCredentialsTokenHandler(
    Handler[IssueClientCredentialsTokenCommand, IssueClientCredentialsTokenResult],
):
    """Authenticate one confidential service client and sign its exact grants."""

    __slots__ = (
        "_access_token_ttl_seconds",
        "_client_credentials_query",
        "_issuer",
        "_secret_processor",
        "_signer",
    )

    def __init__(
        self,
        client_credentials_query: ClientCredentialsQuery,
        secret_processor: OAuthClientSecretProcessor,
        signer: ServiceAccessTokenSigner,
        *,
        issuer: str,
        access_token_ttl_seconds: int,
    ) -> None:
        """Store exact policy and caller-owned authorization adapters."""
        if not issuer.strip() or issuer != issuer.strip():
            raise ValueError("Token issuer must be non-empty and have no outer whitespace")
        if not 60 <= access_token_ttl_seconds <= 3600:
            raise ValueError("Access-token TTL must be between 60 and 3600 seconds")
        self._client_credentials_query = client_credentials_query
        self._secret_processor = secret_processor
        self._signer = signer
        self._issuer = issuer
        self._access_token_ttl_seconds = access_token_ttl_seconds

    async def __call__(
        self,
        input_: IssueClientCredentialsTokenCommand,
        /,
    ) -> IssueClientCredentialsTokenResult:
        """Issue one fresh short-lived RS256 token after exact intersection checks."""
        context = await self._client_credentials_query.get_authorization_context(
            input_.client_id,
        )
        if context is None:
            raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT)

        now = datetime.now(UTC)
        self._authenticate_client(context, input_.client_secret, at=now)
        principal_id, service_slug = self._validate_service_binding(context)

        if OAuthGrantType.CLIENT_CREDENTIALS not in context.grant_types:
            raise GetTokenError(GetTokenErrorCode.UNAUTHORIZED_CLIENT)

        requested_scopes = frozenset(input_.requested_scopes)
        if not requested_scopes or len(requested_scopes) != len(input_.requested_scopes):
            raise GetTokenError(GetTokenErrorCode.INVALID_SCOPE)
        if not (
            requested_scopes.issubset(context.service_scopes)
            and requested_scopes.issubset(context.client_scopes)
        ):
            raise GetTokenError(GetTokenErrorCode.INVALID_SCOPE)
        if not (
            input_.resource in context.service_audiences
            and input_.resource in context.client_audiences
        ):
            raise GetTokenError(GetTokenErrorCode.INVALID_TARGET)

        scopes = tuple(sorted(requested_scopes))
        scope = format_pokerlost_scope_string(scopes)
        expires_at = now + timedelta(seconds=self._access_token_ttl_seconds)
        token = self._signer.sign(
            PokerlostAccessTokenClaims(
                issuer=self._issuer,
                subject=principal_id,
                audience=input_.resource.value,
                issued_at=now,
                not_before=now,
                expires_at=expires_at,
                token_id=uuid4(),
                token_use="access",
                client_id=context.client_id,
                scope=scope,
                principal_type=PrincipalType.SERVICE,
                role=AuthorizationRole.AUTO,
                service_slug=service_slug,
            ),
        )
        return IssueClientCredentialsTokenResult(
            access_token=SecretStr(token),
            expires_in=self._access_token_ttl_seconds,
            scopes=scopes,
        )

    def _authenticate_client(
        self,
        context: ClientCredentialsAuthorizationContext,
        secret: SecretStr,
        *,
        at: datetime,
    ) -> None:
        """Authenticate without disclosing client or credential failure details."""
        if context.client_status is not OAuthClientStatus.ACTIVE:
            raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT)
        if context.client_type is not OAuthClientType.CONFIDENTIAL:
            raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT)
        matches = tuple(
            self._secret_processor.verify(secret, credential.secret_digest)
            for credential in context.credentials
            if credential.accepts_at(at)
        )
        if not any(matches):
            raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT)

    @staticmethod
    def _validate_service_binding(
        context: ClientCredentialsAuthorizationContext,
    ) -> tuple[UUID, str]:
        """Require the exact active service/auto principal bound to the client."""
        if (
            context.bound_principal_id is None
            or context.principal_id is None
            or context.bound_principal_id != context.principal_id
            or context.principal_type is not PrincipalType.SERVICE
            or context.principal_role is not AuthorizationRole.AUTO
            or context.principal_status is not PrincipalStatus.ACTIVE
            or context.service_slug is None
            or not context.service_slug.strip()
        ):
            raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT)
        return context.principal_id, context.service_slug

# authService

SERVICE_NAME: authService
SERVICE_SLUG: authservice

## Purpose

OAuth2 authorization server and token authority for PokerLost.

## Responsibilities

- Own authorization principals and principal types.
- Own OAuth2 clients, roles, scopes, role grants, direct service grants and audience grants.
- Own one-time login grants.
- Issue access tokens and human refresh tokens.
- Own human sessions, refresh-token families and revocation state.
- Own service credentials, JWT signing metadata and JWKS publication.
- Provide idempotent authorization-state operations used by accountsService.

## Service-specific rules

- Canonical access categories are `public`, `user`, `support`, `master` and `auto`.
- `public` means unauthenticated access; it is not a persisted role, principal, scope or token claim.
- Human principals use exactly `user`, `support` or `master`.
- Service principals use exactly `auto`.
- Password hashes, Argon2id policy, password verification, usernames, nicknames and account lifecycle belong to accountsService.
- Runtime authorization uses explicit OAuth2 scopes, never role checks.
- Roles have no implicit inheritance; each role owns a complete explicit scope bundle.
- `master` is not a global bypass.
- `auto` does not imply access to every internal operation; service access requires direct scope and audience grants.
- Protected FastAPI operations declare scopes through `Security(..., scopes=[...])`.
- PokerLost inter-service calls use generated `pypokerlost` clients and response types; no direct HTTP fallback is allowed.
- Downstream services validate short-lived JWT access tokens locally and do not call authService per request.
- Human login uses a one-time, digest-only login grant exchanged at `/oauth.token`; raw passwords never enter authService.
- `/oauth.token` returns standard OAuth2 token and error payloads rather than `ApplicationResponse`.
- Human refresh tokens are opaque, stored as digests, rotated on every use and protected by reuse detection.
- Service principals use `client_credentials`, receive no human session and receive no refresh token.
- JWT signing uses RS256 with mandatory `kid`; private keys are mounted secrets and JWKS retains public keys for safe rotation.
- Principal disablement and human role changes revoke active sessions and refresh-token families; already-issued access tokens remain valid only until their short expiry unless a future revocation-distribution mechanism is introduced.

## Operation identifiers

- PokerLost operation identifiers use `namespace.someOperation`, where both the stable namespace and operation use lowerCamelCase.
- Operation paths are exactly the operation identifier prefixed with `/`.
- The shared authorization operations are `principals.provisionHuman`, `principals.setStatus`, `principals.assignRole` and `loginGrants.issue`, with paths `/principals.provisionHuman`, `/principals.setStatus`, `/principals.assignRole` and `/loginGrants.issue`.
- OAuth2 scope identifiers are separate lowercase dotted values and retain names such as `auth.internal.provision_human`.

## Initial protocol profile

- Human login grant: `urn:pokerlost:params:oauth:grant-type:login-grant`.
- Refresh: `refresh_token`.
- Service authentication: `client_credentials`.
- Password, implicit, device, OIDC and social-login grants are not implemented in the first production version.

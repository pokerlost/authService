# authService

SERVICE_NAME: authService
SERVICE_SLUG: authservice

## Purpose

Pokerlost token authority and authorization-state owner.

The public wire contract is the private Pokerlost JSON protocol over HTTPS. It is not an OAuth2,
Bearer, Basic, or header-authentication protocol. Existing OAuth-named persistence objects remain
internal implementation details.

## Responsibilities

- Own authorization principals and principal types.
- Own clients, roles, scopes, role grants, direct service grants and audience grants.
- Own one-time login grants as a future business stage.
- Issue short-lived service access tokens from body-supplied client credentials.
- Own future human sessions, refresh-token families and revocation state.
- Own service credentials and JWT signing metadata; JWKS publication is deferred.
- Provide future idempotent authorization-state operations used by accountsService.

## Service-specific rules

- Canonical access categories are `public`, `user`, `support`, `master` and `auto`.
- `public` means unauthenticated access; it is not a persisted role, principal, scope or claim.
- Human principals use exactly `user`, `support` or `master`; service principals use `auto`.
- Password hashes, password verification, usernames, nicknames and account lifecycle belong to
  accountsService.
- Runtime authorization uses exact Pokerlost scopes, never role checks or wildcard grants.
- Roles have no implicit inheritance; `master` is not a bypass and `auto` grants no scopes.
- Downstream services validate short-lived JWT access tokens locally and do not call authService
  for each protected request.
- Pokerlost inter-service calls use `pypokerlost`; no direct HTTP fallback is allowed.
- authService does not instantiate a client to itself or accountsService.
- Existing applied migrations are immutable; persisted scope spelling changes use forward
  migrations.

## Current service-client profile

- `authservice bootstrap-service-client` is the operator bootstrap boundary.
- Bootstrap creates one active service principal, one bound confidential client, exact direct and
  client scope grants, exact service and client audience grants, and one digest-only credential.
- `POST /getToken` is the only implemented business operation.
- Its request is `PokerlostRequest[GetTokenRequest]` JSON with `client_id`, `client_secret`, exact
  `scopes`, and logical service `audience` inside `payload`.
- Authentication material is accepted only in the JSON body. No caller-supplied authentication
  header, cookie, query parameter, form body, or token type prefix is accepted.
- The logical audience, such as `authService`, is mapped at the application boundary to the
  existing internal `urn:pokerlost:service:<audience>` grant representation.
- Success returns `PokerlostResponse[PokerlostToken]`; failures return
  `PokerlostResponse[None]`. Retry delay, when applicable, is represented only by
  `PokerlostResponse.retry_after`.
- A service token is short-lived, contains service-only claims, and is not persisted.
- The current flow creates no human session or refresh token.

## Operation identifiers

- Operation identifiers match `^[a-z][A-Za-z0-9]*$` and paths are `/<operationId>`.
- Current business operation: `getToken` at `POST /getToken`.
- Reserved future SDK operations are `refreshToken`, `getJwks`, `provisionHuman`,
  `setPrincipalStatus`, `assignPrincipalRole`, and `issueLoginGrant`; they are not current server
  endpoints.
- Scope identifiers remain separate dotted lowerCamelCase values, for example
  `auth.internal.provisionHuman` and `auth.internal.assignPrincipalRole`.

## Non-goals of the current stage

Human login-grant exchange, refresh tokens, sessions, logout, JWKS publication, principal HTTP
operations, retained signing keys, and signing-key rotation are not implemented.

# authService

`authService` is PokerLost's source of truth for identities, credentials, authentication sessions,
OAuth2 scope grants, access and refresh tokens, JWT verification metadata, service credentials,
registered OpenAPI authorization contracts, and durable security audit events. It is not a gateway
or proxy. Resource services validate access JWTs locally and do not call authService for each RPC.

This repository implements the frozen first-production OAuth2 profile from AUTH-09. PostgreSQL is
the only required stateful dependency. Redis, an access-token denylist, email password recovery,
OIDC, browser authorization flows, and social identity federation are outside this version.

## Authorization model

Roles classify principals as `user`, `support`, `master`, or `auto`; they are not runtime
permissions. Runtime authorization uses OAuth2 scopes exclusively:

```text
human Role
    -> explicit RoleScopeGrant
    -> OAuth2 access-token scope claim
    -> FastAPI SecurityScopes
    -> exact RPC operation scope

ServicePrincipal
    -> ServiceAudienceGrant + explicit ServiceScopeGrant
    -> client_credentials grant
    -> audience-isolated machine JWT scopes
```

There is no implicit role inheritance or administrator bypass. Every grant is an explicit database
row. `auto` is rejected by role-scope management and receives only service scopes for a specific
target audience. A machine token requires both the coarse audience grant and every requested scope
grant.

The canonical PokerLost v1 invariant is:

```text
OAuth2 scope == OpenAPI operationId
```

Aliases such as `admin`, `user`, or `balance:read` are not API authorization scopes. Public is not
a role and is represented by `security: []`.

Human access JWTs contain `iss`, `sub`, `aud`, `iat`, `nbf`, `exp`, `jti`, `token_use=access`,
`role`, `sid`, and a space-delimited `scope`. Machine JWTs contain the same standard temporal and
identity claims plus `role=auto`, `service`, and `scope`, but no `sid`; their `aud` is the requested
resource service slug. The `role` claim remains useful for identity classification and audit
context, never as the final permission check.

## OAuth2 token endpoint

All token issuance uses one RPC endpoint:

```text
POST /oauth.token
operationId: authService.oauth.token
content-type: application/x-www-form-urlencoded
```

It supports this PokerLost OAuth2 server profile:

- `grant_type=password` with `username`, `password`, and optional `scope`;
- `grant_type=refresh_token` with `refresh_token` and optional `scope`;
- `grant_type=client_credentials` with optional `scope`, required `resource`, and HTTP Basic client
  authentication.

The profile does not claim OAuth 2.1 conformance because it intentionally supports password grant.
It also deliberately wraps the token result in `ApplicationResponse`, so it is not drop-in wire
compatible with clients that require a naked RFC token response.

An omitted password scope grants all currently active scopes explicitly granted to the principal's
exact role. A human session stores that initial scope snapshot as its permanent ceiling. Refresh
may preserve or narrow that ceiling, intersected with current role grants; it can never broaden it.
A revoked role grant therefore disappears on the next refresh while an already issued short-lived
JWT remains valid until expiration.

An omitted client-credentials scope grants all currently active scopes explicitly granted to the
source service principal for the requested resource. Machine credentials never receive refresh
tokens.

Successful token results have standard inner field meanings:

```json
{
  "ok": true,
  "result": {
    "access_token": "<access-token>",
    "token_type": "Bearer",
    "expires_in": 600,
    "scope": "authService.sessions.list authService.auth.logout",
    "refresh_token": "<refresh-token>"
  },
  "error": null,
  "errorMessage": null
}
```

Grant failures use the same envelope and stable codes such as `AUTH_OAUTH_INVALID_GRANT`,
`AUTH_OAUTH_INVALID_CLIENT`, `AUTH_OAUTH_INVALID_SCOPE`, and
`AUTH_OAUTH_UNSUPPORTED_GRANT_TYPE`. Missing or invalid Bearer tokens return 401 with
`AUTH_INVALID_ACCESS_TOKEN`; a valid token missing an operation scope returns 403 with
`AUTH_INSUFFICIENT_SCOPE`.

## API surface

Every user-defined FastAPI operation returns `ApplicationResponse`, including root, JWKS, the
OpenAPI document, OAuth2 token issuance, and all error paths. Framework documentation endpoints
and the raw OpenAPI endpoint are disabled.

| Method | Path | operationId | Authorization |
|---|---|---|---|
| GET | `/` | `authService.root` | public |
| GET | `/jwks.get` | `authService.jwks.get` | public |
| GET | `/openapi.get` | `authService.openapi.get` | public |
| POST | `/users.register` | `authService.users.register` | public |
| POST | `/oauth.token` | `authService.oauth.token` | OAuth2 grant endpoint |
| POST | `/auth.logout` | `authService.auth.logout` | exact operation scope |
| POST | `/auth.logoutAll` | `authService.auth.logoutAll` | exact operation scope |
| GET | `/sessions.list` | `authService.sessions.list` | exact operation scope |
| POST | `/sessions.revoke` | `authService.sessions.revoke` | exact operation scope |
| POST | `/account.changePassword` | `authService.account.changePassword` | exact operation scope |
| POST | `/support.getUserAccount` | `authService.support.getUserAccount` | exact operation scope |
| POST | `/master.createSupportAccount` | `authService.master.createSupportAccount` | exact operation scope |
| POST | `/master.createMasterAccount` | `authService.master.createMasterAccount` | exact operation scope |
| POST | `/master.disableAccount` | `authService.master.disableAccount` | exact operation scope |
| POST | `/master.enableAccount` | `authService.master.enableAccount` | exact operation scope |
| POST | `/master.resetHumanPassword` | `authService.master.resetHumanPassword` | exact operation scope |
| POST | `/master.registerOpenApiContract` | `authService.master.registerOpenApiContract` | exact operation scope |
| POST | `/master.validateOpenApiContract` | `authService.master.validateOpenApiContract` | exact operation scope |
| POST | `/master.diffOpenApiContract` | `authService.master.diffOpenApiContract` | exact operation scope |
| POST | `/master.activateOpenApiContract` | `authService.master.activateOpenApiContract` | exact operation scope |
| POST | `/master.retireOpenApiContract` | `authService.master.retireOpenApiContract` | exact operation scope |
| GET | `/master.listRegisteredServices` | `authService.master.listRegisteredServices` | exact operation scope |
| POST | `/master.getRegisteredService` | `authService.master.getRegisteredService` | exact operation scope |
| POST | `/master.listOpenApiContracts` | `authService.master.listOpenApiContracts` | exact operation scope |
| POST | `/master.getOpenApiContract` | `authService.master.getOpenApiContract` | exact operation scope |
| POST | `/master.getAuthorizationManifest` | `authService.master.getAuthorizationManifest` | exact operation scope |
| POST | `/master.createAutoPrincipal` | `authService.master.createAutoPrincipal` | exact operation scope |
| POST | `/master.createServiceCredential` | `authService.master.createServiceCredential` | exact operation scope |
| POST | `/master.revokeServiceCredential` | `authService.master.revokeServiceCredential` | exact operation scope |
| POST | `/master.grantServiceAudience` | `authService.master.grantServiceAudience` | exact operation scope |
| POST | `/master.revokeServiceAudience` | `authService.master.revokeServiceAudience` | exact operation scope |
| POST | `/master.grantRoleScope` | `authService.master.grantRoleScope` | exact operation scope |
| POST | `/master.revokeRoleScope` | `authService.master.revokeRoleScope` | exact operation scope |
| GET | `/master.listRoleScopes` | `authService.master.listRoleScopes` | exact operation scope |
| POST | `/master.grantServiceScope` | `authService.master.grantServiceScope` | exact operation scope |
| POST | `/master.revokeServiceScope` | `authService.master.revokeServiceScope` | exact operation scope |
| POST | `/master.listServiceScopes` | `authService.master.listServiceScopes` | exact operation scope |
| POST | `/master.listAuditEvents` | `authService.master.listAuditEvents` | exact operation scope |

`/openapi.json`, `/docs`, `/redoc`, and `/.well-known/jwks.json` are not registered. Consumers use
`GET /openapi.get` and unwrap `result.document`; JWKS consumers use `GET /jwks.get` and unwrap
`result`.

## Explicit authService seed grants

Migration `20260824_0006` creates individual rows without wildcards:

- `user`: `authService.auth.logout`, `authService.auth.logoutAll`,
  `authService.sessions.list`, `authService.sessions.revoke`, and
  `authService.account.changePassword`;
- `support`: all five human-session scopes plus `authService.support.getUserAccount`;
- `master`: all five human-session scopes, `authService.support.getUserAccount`, and every current
  `authService.master.*` operation scope.

Activation of another service contract creates operation ownership and authorization requirements,
but grants no role or service access automatically.

## OpenAPI authorization contract

Only JSON documents are accepted and published. Every contract has a top-level service identity:

```json
{
  "x-pokerlost-service": {
    "id": "virtualMoney"
  }
}
```

Public operations have empty effective security:

```json
{
  "operationId": "virtualMoney.root",
  "security": []
}
```

Each protected operation has exactly one canonical OAuth2 requirement and one scope equal to its
operation ID:

```json
{
  "operationId": "virtualMoney.balance.get",
  "security": [
    {
      "OAuth2": [
        "virtualMoney.balance.get"
      ]
    }
  ]
}
```

`components.securitySchemes.OAuth2` must have `type: "oauth2"`, password and client-credentials
flows, token URL `/oauth.token`, and a scope catalog containing every protected owned operation.
The registry normalizes each `ApiOperationModel` to either `public` with no required scope or
`oauth2` with `required_scope == api_operation_id`. The manifest contains no role lists.

A contract transition from public to OAuth2 is tightening. OAuth2 to public is weakening and
requires explicit acknowledgement. Contract activation never changes role or service grants.

## Password lifecycle

`POST /account.changePassword` verifies the current Argon2id password, hashes the new password,
updates `password_changed_at`, revokes every session and refresh token including the current
session, and appends the audit event in the same transaction. A fresh password grant is required.

`POST /master.resetHumanPassword` is protected by its exact master operation scope, accepts only a
different human principal, replaces the password hash, and revokes all target sessions and refresh
tokens atomically with its audit event. There is no email or reset-token flow.

## Durable security audit

`AuditEventModel` is append-only and stores event type/result, safe actor and target identifiers,
request/correlation/operation context, occurrence time, and bounded safe JSON metadata. Passwords,
hashes, usernames, nicknames, tokens, secrets, credential digests, peppers, private keys,
Authorization values, and full OpenAPI documents are forbidden.

Successful security mutations append their events in the same PostgreSQL transaction, so an audit
insert failure rolls back the mutation. Failed password and client authentication return an error
result instead of raising, allowing limiter state and the audit event to commit durably in the
request transaction. A dedicated audit transaction is used only when the business transaction must
roll back. Refresh-token reuse revocation and its audit event commit together.

`POST /master.listAuditEvents` provides bounded keyset pagination. Cleanup may remove events only
after `audit_retention_days`.

## Rate limiting and retention

Password and client-credential brute-force state is persisted in PostgreSQL and updated under row
locking, so it remains correct across service instances. Limiter keys are fingerprints; raw
usernames, passwords, and client secrets are never stored. Limits, windows, and lock durations are
bounded settings. Exceeded attempts return 429 `AUTH_RATE_LIMITED` without revealing whether an
account exists.

OAuth2 scope requests are bounded by count, individual token length, total claim bytes, and final
JWT bytes. Only currently active and explicitly granted scopes can be issued.

Run bounded retention cleanup in dry-run mode by default:

```bash
uv run authservice maintenance cleanup
uv run authservice maintenance cleanup --apply
```

Cleanup covers eligible refresh-token leaves, sessions without retained refresh state, expired or
revoked service credentials, stale limiter rows, and old audit events. It never deletes operation
ownership, OpenAPI history, or scope grants.

## Operator commands

Bootstrap the first master using hidden password input:

```bash
uv run authservice master create
```

Manage OAuth2 grants through the same application handlers used by HTTP control-plane operations:

```bash
uv run authservice oauth grant-role-scope support virtualMoney.balance.get
uv run authservice oauth revoke-role-scope support virtualMoney.balance.get
uv run authservice oauth grant-service-scope pokerserver virtualmoney virtualMoney.holds.create
uv run authservice oauth revoke-service-scope pokerserver virtualmoney virtualMoney.holds.create
```

AUTO provisioning and audience management remain operator-accessible:

```bash
uv run authservice auto create-principal pokerserver
uv run authservice auto create-credential pokerserver
uv run authservice auto grant-audience pokerserver virtualmoney
uv run authservice auto revoke-audience pokerserver virtualmoney
uv run authservice auto revoke-credential <client-id>
```

Only credential creation reveals a new client secret, once.

## Development

Install locked dependencies and run quality checks:

```bash
uv sync --locked --all-groups
make format
make lint
make typecheck
make pre-commit
python -m compileall -q app alembic/env.py
```

Run migrations explicitly; startup never migrates the database:

```bash
make db-upgrade
uv run alembic current
uv run alembic heads
uv run alembic check
```

`20260824_0006` performs the pre-freeze OAuth2 transition. It creates role/service/session scope
state, replaces the role-policy registry schema, retires legacy active contracts, preserves raw
contract history and permanent operation ownership, seeds authService operations and grants, and
revokes scope-less legacy human sessions and refresh tokens. Downgrade restores schema shape but
intentionally does not resurrect revoked runtime state. `20260824_0007` creates durable audit and
PostgreSQL rate-limit state.

## Configuration and deployment

Configuration uses the `AUTH_` prefix and nested `__` keys. Required production secrets include
the database URL, refresh-token pepper, service-credential pepper, and an RSA private signing key
mounted outside the image. OAuth2 limits, rate-limit policy, and retention settings are validated
at startup. Unsafe production defaults fail fast.

The multi-stage Docker image installs locked dependencies, excludes signing keys and peppers, runs
as UID/GID `10001`, and starts Gunicorn with `uvicorn_worker.UvicornWorker`. Helm references
existing Secrets for PostgreSQL, Logfire, peppers, and signing keys; non-secret OAuth2/rate-limit/
retention values are supplied through the ConfigMap. Health probes use wrapped `GET /`.

Logfire is configured without request-header, argument, or request-body capture. Sensitive field
patterns are scrubbed and Authorization is not recorded. CORS is disabled because no browser
cross-origin contract exists. Arbitrary forwarded headers are not trusted.

## Deferred beyond the first-production freeze

Authorization-code, implicit, device-code, OIDC, social/federated login, MFA, passkeys/WebAuthn,
email recovery, Redis-backed infrastructure, access-token denylisting, composite operation scopes,
and background cleanup workers are deliberately deferred. Resource-domain authorization remains
owned by the relevant resource service.

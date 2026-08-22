# authService

`authService` is PokerLost's source of truth for authentication principals, human credentials,
authentication state, and explicit coarse-grained roles. It is not an API gateway or reverse
proxy, and ordinary platform RPC calls do not synchronously pass through it.

AUTH-03 adds RS256 human access-token signing, mounted-key validation, and rotation-safe JWKS
publication to the AUTH-02 foundation. Login, persistent sessions, refresh rotation, password
recovery, machine credentials, and runtime authorization enforcement are not implemented yet.

## Architecture

The source root is `app/` and is placed directly on `PYTHONPATH`:

```text
FastAPI router
-> Pydantic Request
-> application Command
-> Handler
-> concrete SQLAlchemy repositories
-> PostgreSQL
```

`api.application.create_app()` loads typed settings, configures Logfire, creates FastAPI,
registers exception handlers and routers, installs lazy OpenAPI generation, and instruments
FastAPI. It does not create SQLAlchemy resources.

Application lifespan creates the async engine and session factory, instruments the concrete
engine, stores resources and settings separately in `app.state`, and disposes the engine
during shutdown. Engine construction belongs to `persistence.database.session`.

## Role model

Every principal has exactly one direct role:

```text
user
support
master
auto
```

There is no implicit role inheritance. Public registration always creates `role=user`;
clients cannot provide a role or status. Support, master, and auto provisioning are outside
AUTH-02.

A principal status is either `active` or `disabled`. Registration creates an active
principal.

## RPC API

| Method | Path | Operation ID | Authorization | Purpose |
| --- | --- | --- | --- | --- |
| `GET` | `/health.checkLiveness` | `authService.health.checkLiveness` | public | Process liveness without PostgreSQL |
| `GET` | `/health.checkReadiness` | `authService.health.checkReadiness` | public | Lightweight PostgreSQL readiness |
| `POST` | `/users.register` | `authService.users.register` | public | Register an ordinary user |

OpenAPI contains:

```yaml
x-pokerlost-service:
  id: authService
```

Each public operation explicitly declares `x-pokerlost-authz.public=true`.

## Registration

Request:

```json
{
  "email": "user@example.com",
  "password": "a sufficiently long password"
}
```

Unknown fields are rejected. The password is represented as `SecretStr` at validated
transport and command boundaries.

The handler normalizes the email case-insensitively, hashes the password using Argon2id, inserts an
active user principal, inserts the unique human account, and stores the encoded credential in one
request-owned transaction. PostgreSQL uniqueness and `INSERT ... ON CONFLICT DO NOTHING
RETURNING` make duplicate detection race-safe.

Success returns only principal metadata:

```json
{
  "ok": true,
  "result": {
    "id": "00000000-0000-0000-0000-000000000000",
    "role": "user",
    "status": "active",
    "createdAt": "2026-08-22T00:00:00Z",
    "updatedAt": "2026-08-22T00:00:00Z"
  }
}
```

Duplicate normalized email returns HTTP `409` with
`AUTH_EMAIL_ALREADY_REGISTERED`. Passwords, hashes, normalized emails, and internal
credential state are never returned.

## Response and request context

Every public response uses exactly:

```text
ok
result
error
errorMessage
```

Success cannot contain error metadata. Failure requires both error fields and cannot contain a
result.

The server generates `X-Request-ID` and accepts only syntactically valid
`X-Correlation-ID`. Identifiers are propagated through response headers and Logfire context;
they are not part of the business response envelope. Client-provided request IDs are ignored.

## Persistence and transactions

AUTH-02 creates:

```text
principals
human_accounts
password_credentials
```

`human_accounts.normalized_email` is unique. Human accounts and credentials use their
principal ID as both primary key and cascading foreign key. Principal role and status values are
protected by database checks.

One parameterized request owns one PostgreSQL transaction:

```python
async with session_factory.begin() as session:
    yield session
```

Handlers and repositories never call `commit()`, `rollback()`, or `begin()`.
Registration conflict raises a semantic application error, causing automatic rollback of the
already inserted principal.

Repositories use explicit `INSERT`, `RETURNING`, and PostgreSQL conflict handling. ORM
mappings do not use Active Record behavior.

## Password hashing

`argon2-cffi` provides Argon2id hashing. Cost parameters are validated under
`AUTH_PASSWORD__*` and default to:

```text
time_cost=3
memory_cost_kib=65536
parallelism=4
hash_length=32
salt_length=16
```

The hashing component supports `hash`, `verify`, and `needs_rehash`. Plaintext
passwords and encoded hashes are excluded from logs and API responses.

## Configuration and observability

Configuration is loaded through one immutable `configuration.Settings` root. PostgreSQL URL
and Logfire token values use `SecretStr`; validation errors hide submitted input. Production
requires remote Logfire delivery.

Logfire is configured before FastAPI construction. FastAPI instrumentation excludes headers and
validated endpoint arguments, and SQLAlchemy instrumentation is attached to the lifespan-owned
engine. Scrubbing covers credentials, cookies, tokens, private keys, DSNs, and database URLs.

## Local and production commands

Requirements are Python 3.12+, `uv`, and PostgreSQL.

```bash
make install
make run
make serve
make format
make lint
make typecheck
make pre-commit
```

Local Uvicorn and production Gunicorn both invoke `api.application:create_app` as an
application factory. Production does not use Typer or an import-time ASGI object.

## Migrations

```bash
make db-upgrade
make db-downgrade
make db-revision message="describe change"
```

Migration `20260822_0001` is the first schema revision and creates only AUTH-02 principal,
human account, and password credential storage. Migrations do not run during application startup.

## Docker and Helm

The multi-stage image uses locked runtime dependencies, runs as UID/GID `10001`, and invokes
the Gunicorn application factory in exec form. Gunicorn process settings remain deployment
settings through `GUNICORN_CMD_ARGS`.

The Helm chart references existing Secrets for PostgreSQL and Logfire. It does not create secrets,
PostgreSQL, or automatic migration jobs. Health probes retain the dotted authService RPC paths.

## Access JWT signing and JWKS

AUTH-03 adds RS256 signing for short-lived human access tokens and publishes the corresponding
public verification keys. It does not add login, session persistence, refresh tokens, logout,
machine credentials, service-token issuance, or runtime endpoint authorization.

The filesystem signing-key provider is created during application lifespan. Startup fails before
the service accepts traffic when the active private key is missing, unreadable, not an RSA private
key, weaker than 2048 bits, or inconsistent with the published public keys. Retained public-key
files are also validated as RSA keys of at least 2048 bits. A filename stem is its validated
`kid`; duplicate identifiers are rejected.

The human access-token header is:

```json
{
  "alg": "RS256",
  "kid": "<active-key-id>",
  "typ": "at+jwt"
}
```

The minimal claim contract is:

```json
{
  "iss": "<configured-issuer>",
  "sub": "<principal-uuid>",
  "aud": "<configured-human-audience>",
  "iat": 0,
  "nbf": 0,
  "exp": 0,
  "jti": "<unique-token-uuid>",
  "token_use": "access",
  "role": "user",
  "sid": "<future-session-uuid>"
}
```

Only the direct human roles `user`, `support`, and `master` can be issued by this component.
The `auto` role is rejected. No role implies another role. Tokens contain no email, profile,
credential, permission, balance, IP-address, user-agent, or other business data.

Public verification material is available as a raw standard document from
`GET /.well-known/jwks.json`. The operation ID is `authService.jwks.get`, the operation is marked
with `x-pokerlost-authz.public=true`, and successful responses use a short configurable public
cache lifetime. The document contains only RSA `kty`, `kid`, `use`, `alg`, `n`, and `e` values.

### JWT configuration

The `AUTH_JWT__*` environment group contains:

- `ISSUER`: access-token issuer.
- `HUMAN_AUDIENCE`: audience for human access tokens.
- `ACCESS_TOKEN_TTL_SECONDS`: bounded short-lived token lifetime; default 600 seconds.
- `CLOCK_SKEW_SECONDS`: bounded verification leeway for future local verifiers.
- `ACTIVE_KID`: stable identifier for the active signing key.
- `ACTIVE_PRIVATE_KEY_PATH`: mounted active RSA private-key file.
- `RETAINED_PUBLIC_KEY_DIRECTORY`: directory containing published RSA public-key files.
- `JWKS_CACHE_TTL_SECONDS`: bounded JWKS `Cache-Control` lifetime.

### Local temporary key

The following key is for local development only. Never commit generated keys or copy a production
private key into the repository or image.

```bash
mkdir -p .local-secrets/auth/public
openssl genpkey \
  -algorithm RSA \
  -pkeyopt rsa_keygen_bits:2048 \
  -out .local-secrets/auth/active-private.pem
openssl pkey \
  -in .local-secrets/auth/active-private.pem \
  -pubout \
  -out .local-secrets/auth/public/key-20260822-a.pem
chmod 600 .local-secrets/auth/active-private.pem
```

Set `AUTH_JWT__ACTIVE_KID=key-20260822-a` and use the local paths shown in `.env.example`.
The entire `.local-secrets/` directory is ignored by Git.

Production keys come from external secret management. The Helm chart references an existing
Kubernetes Secret and mounts its configured items read-only. The chart does not generate a key,
store PEM data in values or a ConfigMap, or copy signing material into the image.

### Rotation

Use this publication order so already issued access tokens remain verifiable:

1. Keep key A active and publish A; tokens are signed with A.
2. Add public keys A and B to the mounted published-key directory.
3. Mount B as the active private key and set `ACTIVE_KID` to B; restart the application.
4. Sign new tokens with B while JWKS continues to publish A and B.
5. Remove A only after its maximum access-token lifetime plus an operator safety window.

# Configuration

This page documents the service settings groups and their environment variable mapping.

`Settings` loads `.env` and process environment values with the `AUTHSERVICE_` prefix.
Nested fields use a double underscore, so the general form is:

```text
AUTHSERVICE_<GROUP>__<FIELD>
```

For example, `database.url` maps to `AUTHSERVICE_DATABASE__URL`. Names are
case-insensitive, but `.env.example` uses uppercase names consistently. Process environment values
override values from `.env` according to Pydantic Settings behavior.

## Base operations

| Field | Environment variable | Required | Example |
| --- | --- | --- | --- |
| `root_operation` | `AUTHSERVICE_ROOT_OPERATION` | Yes | `getRoot` |
| `openapi_operation` | `AUTHSERVICE_OPENAPI_OPERATION` | Yes | `getOpenApi` |

Both fields use `pypokerlost.types.PokerlostOperation`, so invalid startup values fail validation. The
root operation controls only the operation ID for `GET /`; the HTTP path remains `/`. The OpenAPI
operation controls both its operation ID and its `"/" + operation_id` path. Business operation IDs
remain source-defined stable contracts rather than environment settings.

The Helm values `rootOperation` and `openapiOperation` map explicitly to those exact two
environment variables in the ConfigMap. They are not Kubernetes Secrets.

## `application`

| Field | Environment variable | Purpose |
| --- | --- | --- |
| `environment` | `AUTHSERVICE_APPLICATION__ENVIRONMENT` | Deployment category such as `local`, `development`, `staging`, or `production`. |
| `version` | `AUTHSERVICE_APPLICATION__VERSION` | SemVer service contract version published in OpenAPI and telemetry. |

Production configuration fails at startup unless Logfire and remote delivery are enabled.

## `http`

| Field | Environment variable | Purpose |
| --- | --- | --- |
| `host` | `AUTHSERVICE_HTTP__HOST` | Local HTTP bind address. |
| `port` | `AUTHSERVICE_HTTP__PORT` | Local HTTP port from `1` through `65535`. |

## `token`

| Field | Environment variable | Purpose |
| --- | --- | --- |
| `issuer` | `AUTHSERVICE_TOKEN__ISSUER` | Required exact, non-empty service-token issuer. |
| `access_token_ttl_seconds` | `AUTHSERVICE_TOKEN__ACCESS_TOKEN_TTL_SECONDS` | Service access-token lifetime from `60` through `3600` seconds. |

The example TTL is `600` seconds. The issuer is copied exactly into the JWT `iss` claim and is not
silently normalized.

## `jwt`

| Field | Environment variable | Purpose |
| --- | --- | --- |
| `private_key_path` | `AUTHSERVICE_JWT__PRIVATE_KEY_PATH` | Required filesystem path to the mounted PEM private key. |
| `key_id` | `AUTHSERVICE_JWT__KEY_ID` | Required JWT `kid` containing only safe ASCII token characters. |

`key_id` is between one and 128 characters and uses only ASCII letters, digits, `.`, `_`, and `-`.
The path is configuration, not key material. Settings parsing does not read the file; application
lifespan loads it once while constructing the signer and fails startup when it is missing, is not a
PEM RSA private key, or uses an RSA key smaller than 2048 bits. The RS256 algorithm is a code
invariant and is not configurable.

## `database`

| Field | Environment variable | Purpose |
| --- | --- | --- |
| `url` | `AUTHSERVICE_DATABASE__URL` | Required complete `postgresql+asyncpg` SQLAlchemy URL. |
| `pool_size` | `AUTHSERVICE_DATABASE__POOL_SIZE` | Persistent connection-pool size. |
| `max_overflow` | `AUTHSERVICE_DATABASE__MAX_OVERFLOW` | Additional temporary connections allowed above the pool size. |
| `pool_timeout_seconds` | `AUTHSERVICE_DATABASE__POOL_TIMEOUT_SECONDS` | Maximum wait for a pooled connection. |
| `command_timeout_seconds` | `AUTHSERVICE_DATABASE__COMMAND_TIMEOUT_SECONDS` | Asyncpg command timeout. |

The database URL must include a username, password, host, and database. It is treated as a secret and must not appear in logs or committed files.

## `logfire`

| Field | Environment variable | Purpose |
| --- | --- | --- |
| `enabled` | `AUTHSERVICE_LOGFIRE__ENABLED` | Enable Logfire configuration and instrumentation. |
| `send_to_logfire` | `AUTHSERVICE_LOGFIRE__SEND_TO_LOGFIRE` | Send telemetry to the configured remote project. |
| `console` | `AUTHSERVICE_LOGFIRE__CONSOLE` | Render telemetry to the process console. |
| `minimum_level` | `AUTHSERVICE_LOGFIRE__MINIMUM_LEVEL` | Minimum recorded level. |
| `token` | `AUTHSERVICE_LOGFIRE__TOKEN` | Optional write token, required when remote delivery is enabled. |

Keep the signing private key, Logfire token, and database URL outside source control. Kubernetes
mounts the key from a Secret and supplies the other values through Secret references rather than
the chart ConfigMap; see
`docs/development/containers-and-kubernetes.md`.

## Concrete outbound targets

authService has no outbound target settings, credentials, token storage, or retry
configuration. When `SERVICE.md` declares a real target, add one focused immutable settings group
named for that target and one explicitly named field on root `Settings`. A target base URL and
request timeout are deployment configuration. Token credentials, storage, refresh, requested exact
scopes, and audience remain service-owned and are added only when the implemented use case needs
them.

Do not expose `PokerlostRetryPolicy` values as settings; its transport algorithm is fixed by the
SDK. Do not automatically add authService configuration to every service. The complete ownership
pattern is in `docs/architecture/inter-service-clients.md`.

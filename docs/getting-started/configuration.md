# Configuration

This page documents the generated service settings groups and their environment variable mapping.

`Settings` loads `.env` and process environment values with the `AUTHSERVICE_` prefix.
Nested fields use a double underscore, so the general form is:

```text
AUTHSERVICE_<GROUP>__<FIELD>
```

For example, `database.url` maps to `AUTHSERVICE_DATABASE__URL`. Names are case-insensitive, but
`.env.example` uses uppercase names consistently. Process environment values override values from
`.env` according to Pydantic Settings behavior.

## Base operations

| Field | Environment variable | Required | Example |
| --- | --- | --- | --- |
| `root_operation` | `AUTHSERVICE_ROOT_OPERATION` | Yes | `auth.getRoot` |
| `openapi_operation` | `AUTHSERVICE_OPENAPI_OPERATION` | Yes | `openapi.get` |

Both fields use `pypokerlost.types.APIOperation`, so invalid startup values fail validation. The
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

## `business_operation_fingerprint`

| Field | Environment variable | Default | Secret? |
| --- | --- | --- | --- |
| `secret` | `AUTHSERVICE_BUSINESS_OPERATION_FINGERPRINT__SECRET` | Required by authService | Yes |
| `key_version` | `AUTHSERVICE_BUSINESS_OPERATION_FINGERPRINT__KEY_VERSION` | `1` | No |

The secret must contain at least 32 UTF-8 bytes. authService calls `require_secret()` during
`Settings` validation, so a missing or short secret fails startup. Kubernetes supplies the secret
only through a Secret reference; the key version belongs in the ConfigMap.

The first-version rotation policy is intentionally simple: do not rotate the active fingerprint
key until every retained idempotency record created with the old key has expired or been deleted.
The persisted digest and key version remain together, and a candidate with another version is a
conflict. Removing an old secret does not preserve replay comparison for records created with it.

Keep the fingerprint secret, Logfire token, and database URL outside source control. Kubernetes
supplies them through Secret references rather than the chart ConfigMap; see
`docs/development/containers-and-kubernetes.md`.

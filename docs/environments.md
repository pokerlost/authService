# Runtime environments

`ServiceSettings.environment` selects the deployment environment: `main`, `dev`,
`test` or `local`. Configure `AUTHSERVICE_RUNTIME_ENVIRONMENT`; the default is
`local`. The Python `ServiceSettings(environment=...)` argument takes precedence.
The field continues to serialize as `environment`.

Telemetry uses the separate `AUTHSERVICE_ENVIRONMENT` execution contour:
`local`, `dev`, `ci` or `remote`, defaulting to `local`. The two variables do not
select one another and have no implicit mapping. A Git branch or release version
never selects either setting.

Explicit constructor values take precedence over process environment, an explicitly
selected dotenv file, and a synthetic or configured secrets directory, in that
order. `.env.example` is not loaded automatically. Unprefixed and other-service
runtime environment variables do not select this service's deployment environment.
Invalid values fail native validation before I/O; no network destination is
inferred from an environment name.

Select a separate database, credentials and deployment namespace for each remote
environment. `DATABASE_URL` remains explicit and secret-redacted; setting the
identity alone does not provision, migrate or isolate an existing database.
Existing local volumes and paths are preserved. Remote endpoints are not configured
by this repository. Container callers need an explicit approved routing arrangement;
the SDK's local origin means loopback in the caller's network namespace.

This foundation keeps its existing exact SDK dependency and creates no outbound
client. Runtime selection does not upgrade the SDK or configure its endpoints.
Use the working branch → `test` → `dev` → `main` contribution route and the
[complete development checks](development.md). An environment identity alone does
not establish runtime acceptance or deployment status.

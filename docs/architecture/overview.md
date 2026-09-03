# Architecture overview

This page defines authService layers and dependency direction around its implemented token
authority behavior.

## Dependency direction

The core request dependency direction is:

```text
api
-> application
-> domain

api/application composition
-> persistence adapters

api/application composition
-> target-specific pypokerlost clients

application
-> meaningful service-owned ports

target-specific adapters
-> generated pypokerlost methods

configuration and observability
-> infrastructure concerns

application
-> security and persistence ports
```

`api` owns FastAPI transport and composition. Pydantic request models validate wire input, routes
translate it into application values, and FastAPI response models validate and serialize plain
route results. `application` owns transport-independent use-case
orchestration and builds its typed command, query, and result values on the framework-independent
`domain` foundation.

Composition code supplies concrete persistence adapters where an operation needs them. Application
behavior does not import FastAPI, and domain values do not depend on transport, settings,
observability, or SQLAlchemy. Configuration and observability support the runtime as infrastructure
concerns; they do not own service use cases. The service-owned `security` package implements the
client-secret processing and RS256 signing boundaries without leaking PyJWT or PEM handling into
the application or domain layers.

## Layer responsibilities

| Layer | Responsibility |
| --- | --- |
| `api` | Application factory, lifespan, middleware, dependencies, routes, public schemas, OpenAPI, and safe errors. |
| `application` | Commands, queries, results, meaningful Protocol ports, handler contracts, and concrete use-case orchestration. |
| `domain` | Framework-independent internal values and closed domain or platform categories. |
| `persistence` | SQLAlchemy metadata, sessions, repository execution, and concrete adapters. |
| `configuration` | Typed settings, environment loading, and startup validation. |
| `observability` | Privacy-safe Logfire configuration and FastAPI/SQLAlchemy instrumentation. |
| `security` | Client-secret processing and the PyJWT-backed RS256 signer. |
| `cli` | Operator startup and transactional service-client bootstrap. |

Public request and response models remain API artifacts; ORM models remain persistence artifacts.
When a service needs a read projection, it is a focused persistence artifact. A route performs the
explicit translation between those boundaries rather than sharing one model across layers.

## Runtime foundation

`docs/architecture/request-lifecycle.md` explains composition and per-request flow.
`docs/architecture/persistence-and-transactions.md` defines PostgreSQL session ownership. The API
wire surface is documented separately in `docs/api/overview.md`. When `SERVICE.md` declares a real
outbound target, `docs/architecture/inter-service-clients.md` defines the target-specific SDK
client, middleware, token-store ownership, retry, and lifecycle extension. Inbound local
verification uses the application port described in `docs/api/header-authorization.md`.

The current service owns authorization principals, client/grant persistence, operator bootstrap,
and public JSON `POST /getToken`. Lifespan constructs one process-owned signer; no access token
is persisted. authService has no outbound target, token store, placeholder remote client, or
service-specific retry configuration. See
`docs/architecture/service-client-credentials.md` for the exact ownership rules.

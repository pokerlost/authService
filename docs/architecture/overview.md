# Architecture overview

This page defines the generated service layers and their dependency direction without prescribing
business behavior that belongs to a concrete service.

## Dependency direction

The core request dependency direction is:

```text
api
-> application
-> domain

api/application composition
-> persistence adapters

configuration and observability
-> infrastructure concerns

application
-> security and persistence ports
```

`api` owns FastAPI transport and composition. It translates public schemas into application values
and translates results into API responses. `application` owns transport-independent use-case
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
| `application` | Commands, queries, results, handler contracts, and concrete use-case orchestration. |
| `domain` | Framework-independent internal values and closed domain or platform categories. |
| `persistence` | SQLAlchemy metadata, sessions, repositories, result readers, projections, and concrete adapters. |
| `security` | OAuth client-secret generation and verification plus the PyJWT-backed RS256 signer. |
| `configuration` | Typed settings, environment loading, and startup validation. |
| `observability` | Privacy-safe Logfire configuration and FastAPI/SQLAlchemy instrumentation. |
| `cli` | Operator entry points such as local application startup. |

Public request and response models remain API artifacts; ORM models and projections remain
persistence artifacts. A route performs the explicit translation between those boundaries rather
than sharing one model across layers.

## Runtime foundation

`docs/architecture/request-lifecycle.md` explains composition and per-request flow.
`docs/architecture/persistence-and-transactions.md` defines PostgreSQL session ownership. The API
wire surface is documented separately in `docs/api/overview.md`, and the shared idempotency
primitive is documented in `docs/architecture/business-operation-fingerprinting.md`.

The current checkout adds the service-client credential foundation, a transactional operator
bootstrap command, and `POST /oauth.token` on top of the authorization domain and persistence
foundation. The detailed responsibility split and authorization rules are documented in
`docs/architecture/service-client-credentials.md`.

Consumer services use the `pypokerlost` authentication and outbound middleware pipeline described
in `docs/api/openapi-and-sdk.md`. That client lifecycle remains consumer-owned. authService does not
instantiate an outbound client to itself or accountsService for credential validation, token
issuance, login-grant exchange, refresh, or JWT signing.

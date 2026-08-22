# FastAPI Service Repository Rules — Reusable `AGENTS.md` Template

> Copy this file to the root of a new service repository as `AGENTS.md`.
> Fill in the mandatory **Service Profile** before implementation starts.
> Service-specific rules override the common rules below.

---

# Service Profile — Must Be Completed

```text
SERVICE_NAME: <canonical human-facing name, e.g. authService>
SERVICE_SLUG: <lowercase DNS/Kubernetes name, e.g. authservice>
SERVICE_PURPOSE: <one paragraph>
SERVICE_ROLE: <AUTH | FINANCIAL | CRYPTO | POKER | GENERAL>
DATA_OWNERSHIP: <data for which this service is the source of truth>
OUT_OF_SCOPE: <explicitly forbidden responsibilities>
PRIMARY_STORAGE: <PostgreSQL | none | another explicitly approved store>
SECONDARY_STORAGE: <Redis or none; explain exact responsibility>
EXTERNAL_DEPENDENCIES: <services, RPC providers, nodes, gateways>
AUTH_POLICY: <owned here | external Auth Service | not yet integrated>
REALTIME_POLICY: <HTTP only | HTTP + WebSocket>
SPECIAL_INVARIANTS: <domain invariants that must never be violated>
FIRST_PRODUCTION_SCOPE: <what must exist before the service is frozen>
```

The Service Profile is not documentation decoration. It defines the service boundary.

Do not silently add responsibilities that are absent from the profile.

When a new requirement conflicts with an older one:

1. state the conflict;
2. apply the newest explicit requirement;
3. update this file and relevant documentation;
4. remove obsolete contradictory rules.

---

# Communication and Repository Language

- Communicate with the repository user in Russian unless they request another language.
- Keep repository-owned code documentation in English:
  - module, class, function, and method docstrings;
  - meaningful comments;
  - OpenAPI summaries and descriptions;
  - settings descriptions;
  - CLI help;
  - developer-facing log messages;
  - README and architecture/deployment documentation.
- Use concise PEP/reStructuredText-style docstrings.
- Do not use Google-style `Args:`, `Returns:`, or `Raises:` sections.
- Do not add docstrings that merely repeat a symbol name.

---

# Scope Discipline

Before changing the repository:

1. read root `AGENTS.md`;
2. inspect the current structure;
3. inspect only files relevant to the task;
4. preserve unrelated user changes;
5. avoid repository-wide cosmetic rewrites;
6. review the final diff before reporting completion.

Do not:

- perform unrelated refactoring;
- invent non-existent paths without inspecting the repository;
- add infrastructure without a current requirement;
- perform destructive Git operations;
- run `git push` unless explicitly requested;
- claim commands passed when they were not executed.

A new abstraction must own an independent responsibility.

Do not create an interface, base class, wrapper, mapper, provider alias, helper, service, registry,
or DTO merely to:

- rename another object;
- forward one call;
- remove two explicit lines;
- wrap an existing FastAPI, Pydantic, or SQLAlchemy API without additional semantics;
- provide theoretical future flexibility;
- convert an ORM object to an identical model.

---

# Default Technology Stack

Unless the Service Profile explicitly requires another architecture, use:

```text
Python >= 3.12
FastAPI
Pydantic v2
Pydantic Settings
SQLAlchemy 2.x async ORM
asyncpg
PostgreSQL
Alembic
Typer
Pydantic Logfire
Gunicorn
uvicorn-worker
Uvicorn for local development
Docker
Helm
kind for local Kubernetes development
uv
Ruff
mypy
pre-commit
```

Do not add:

- Redis;
- MongoDB or another NoSQL database;
- another ORM;
- raw-SQL-only persistence;
- message brokers;
- Celery;
- another web framework;
- a second logging/observability stack;

unless a concrete requirement justifies it.

Do not add a dependency only because it may be useful later.

---

# Python Conventions

- Support Python 3.12 and newer.
- Ruff and mypy target Python 3.12.
- Maximum line length is 99.
- Ruff Formatter is the default and only formatter.
- Every maintained project-owned Python module uses:

```python
"""English module documentation."""

from __future__ import annotations
```

- Use Python 3.12 PEP 695 generics where supported.
- Avoid `Any`, broad `cast()`, broad `# type: ignore`, and reflection for known fields.
- Do not use `setattr`, `object.__setattr__`, known-field `getattr`, `vars`, or `__dict__`
  mutation for ordinary project logic.
- Use canonical acronym capitalization:
  - `SQLAlchemy`;
  - `API`;
  - `HTTP`;
  - `UUID`;
  - `ORMSchema`.
- Choose collections by meaning:
  - `list` for ordinary ordered materialization;
  - `set` for uniqueness and membership;
  - `frozenset` for meaningful immutable uniqueness;
  - `tuple` only for a fixed immutable semantic sequence or a library contract.
- Do not create unnecessary intermediate collection conversions.

---

# Source Root, Packages, and Imports

Use:

```text
app/
```

as the Python source root.

`app/` is not an import prefix.

Correct:

```python
from api...
from application...
from configuration...
from domain...
from observability...
from persistence...
```

Forbidden:

```python
from app.api...
from app.application...
```

Local commands use:

```bash
PYTHONPATH=app
```

Containers use the corresponding absolute path, for example:

```text
PYTHONPATH=/service/app
```

Never mutate `sys.path`.

## Package initializers

Every Python package directory under `app/` contains `__init__.py`, even when intentionally empty.

Do not rely on namespace packages inside the service source tree.

## Relative imports

Use relative imports when the import stays inside the current package or addresses a sibling/child.

Good:

```python
from .command import CreateAccountCommand
from .account_status import AccountStatus
from .create import router as create_router
```

Parent-climbing imports are forbidden:

```python
from ..base import ConflictError
```

Use an absolute architectural import instead:

```python
from application.errors.base import ConflictError
```

Imports crossing top-level architecture packages are absolute.

## Package facades

`__init__.py` is an intentional public facade, not an export dump.

Good consumer imports:

```python
from application.accounts import GetAccountQuery
from api.schemas.requests import GetAccountRequest
from domain.enums import AccountStatus
from persistence.repositories import SQLAlchemyAccountRepository
```

Facade files:

- use relative imports;
- expose only symbols with real external consumers;
- keep `__all__` as a tuple;
- avoid circular barrel imports.

Leaf implementation modules normally omit `__all__`.

Root facades such as `application/__init__.py` and `persistence/__init__.py` remain minimal.

---

# Architecture

The default service architecture is:

```text
HTTP Request
    ->
FastAPI action router
    ->
Pydantic Request
    ->
Command or Query
    ->
Handler
    ->
shared business service when genuinely reused
    ->
SQLAlchemy entity repository
or SQLAlchemy read query adapter
    ->
PostgreSQL
```

Composition dependencies are assembled at the API boundary.

A practical dependency direction is:

```text
api composition -> application + persistence
application     -> persistence + domain
persistence     -> domain
configuration / observability -> composition root
```

Do not create circular imports.

Persistence must not import application operations or API schemas.

---

# Recommended Source Layout

Adapt this layout to the service. Do not create empty directories.

```text
app/
    api/
        application.py
        lifespan.py
        openapi.py
        routes.py
        resources.py

        dependencies/
            __init__.py
            database.py
            resources.py
            settings.py

        errors/
            __init__.py
            configure.py
            application.py
            database.py
            validation.py
            unexpected.py

        routers/
            root.py
            <feature>/
                __init__.py
                router.py
                dependencies.py
                <action>.py

        schemas/
            base/
            requests/
            orm/
            responses/

        types/

    application/
        <feature>/
            __init__.py
            <operation>/
                __init__.py
                command.py or query.py
                handler.py
            services/

        errors/
        pagination/

    configuration/
    domain/
        enums/
        errors/
        types/
        value_model.py

    observability/

    persistence/
        database/
            base.py
            session.py
            mixins/
            models/
            result_readers/

        repositories/
        queries/
        projections/

    cli/
```

One public model, enum, request, response, command, query, handler, error, or ORM entity per file
is preferred when it improves navigation.

Do not create giant `services.py`, `models.py`, `errors.py`, `api.py`, `utils.py`, or `common.py`
dumping grounds.

---

# HTTP RPC API Standard

The platform API is intentionally RPC-like.

## Methods

Use:

```text
POST
GET
```

- Every command or query requiring input uses `POST`.
- It receives exactly one documented Pydantic JSON body.
- `GET` is reserved for parameterless endpoints such as `/`.

Do not use `PUT`, `PATCH`, or `DELETE`.

Do not put business identifiers or operation IDs in:

- path parameters;
- custom business headers.

A future authentication token header is a security transport concern and is the explicit exception.

Use `Query` only as a deliberate documented exception.

## Paths

Use dotted camelCase RPC paths:

```text
/accounts.createAccount
/accounts.getAccount
/holds.reserveHold
/tablePositions.cashOut
```

The router's logical area and method name must be explicit.

Every route decorator places `path=` first:

```python
@router.post(
    path="/accounts.getAccount",
    ...
)
```

## OpenAPI operation IDs

Every endpoint declares one stable deterministic `operation_id`.

Convention:

```text
<resource>_<operation_snake_case>
```

Examples:

```text
accounts_get_account
holds_reserve_hold
table_positions_cash_out
```

Paths, operation IDs, JSON field names, requiredness, result schemas, discriminators, and error
meanings are compatibility contracts.

---

# Router Architecture

One router package represents one logical API area.

Each action lives in a focused file.

Example:

```text
api/routers/accounts/
    __init__.py
    router.py
    dependencies.py
    create.py
    get.py
    get_balance.py
```

The base router imports child router objects explicitly:

```python
from .create import router as create_router
from .get import router as get_router

router.include_router(create_router)
router.include_router(get_router)
```

Do not import whole modules only to access `.router`.

Every endpoint declares:

- `path`;
- concrete `response_model`;
- `status_code`;
- English `summary`;
- English `description`;
- stable `operation_id`;
- documented `responses`;
- logical tag.

Routers are thin. They:

1. accept a Request;
2. receive a Handler through DI;
3. map Request to Command/Query;
4. call `handler.execute(...)`;
5. return the result envelope.

Routers do not:

- use `AsyncSession`;
- build SQLAlchemy statements;
- commit or roll back;
- calculate business state;
- implement idempotency;
- perform persistence mapping.

---

# Response Contract

Use exactly one public response envelope:

```python
class ApplicationResponse(...):
    ok: bool
    result: T | None
    error: str | None
    error_message: str | None
```

Do not include HTTP status code in JSON.

Success:

```json
{
  "ok": true,
  "result": {}
}
```

Failure:

```json
{
  "ok": false,
  "result": null,
  "error": "STABLE_ERROR_CODE",
  "errorMessage": "Safe English message"
}
```

Ordinary handlers return explicit multiline dictionaries:

```python
return {
    "ok": True,
    "result": result,
}
```

Do not create:

- response factories;
- response builders;
- `_json_response`;
- serialization-only wrappers.

Do not call `.model_validate()` or `.model_dump()` in handlers solely for FastAPI serialization.

Central API exception handlers may construct `JSONResponse` directly.

Prefer FastAPI public imports over equivalent Starlette imports.

---

# Pydantic Model Boundaries

Use Pydantic v2 for structured validated data:

- HTTP Requests;
- ORM response schemas;
- calculated/composite Responses;
- Commands;
- Queries;
- application structured results;
- pagination values;
- read projections;
- domain value objects;
- Settings.

Do not use Pydantic for:

- SQLAlchemy mapped entities;
- repository classes;
- handler/service classes;
- engine/session/runtime resources.

## API schema groups

```text
api/schemas/requests/
api/schemas/orm/
api/schemas/responses/
```

### Requests

- JSON body models only;
- camelCase aliases;
- unknown fields forbidden;
- English field documentation;
- transport validation;
- optional trivial `to_command()` or `to_query()` mapping only.

### ORM schemas

Direct entity output contracts.

They inherit one shared `ORMSchema` with:

```python
ConfigDict(from_attributes=True)
```

Only `ORMSchema` owns shared ORM attribute serialization.

### Responses

Calculated, composite, history, pagination, or union results that are not one ORM entity.

Do not use ORM models as public response contracts.

FastAPI may receive an ORM object inside `result`, but the declared `response_model` remains the
public contract and filters output fields.

---

# Internal Structured Models

Use one immutable alias-free Pydantic base for application/domain values, for example:

```python
class ValueModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        validate_default=True,
    )
```

Use it for:

- Commands;
- Queries;
- value objects;
- ledger drafts;
- posting values;
- pagination values;
- structured internal results.

Do not add API camelCase aliases to internal values.

Avoid dataclass plus manual `__post_init__` validation when Pydantic expresses the invariant more
clearly.

Keep database-state business rules outside model validators.

---

# Semantic Validated Types

Centralize repeated primitive validation.

Examples:

```text
NonNilUUID
OperationId
PositiveMoneyMinor
NonNegativeMoneyMinor
NonZeroMoneyMinor
AssetCode
ReferenceType
UtcDatetime
PayloadFingerprint
RefundReason
```

A semantic type:

- has one clear meaning;
- owns its validator in the same module;
- is reused across Requests, Commands, Queries, and value models.

Do not repeat `AfterValidator(...)` across models.

Do not create aliases that add no semantic validation or meaning.

---

# Application Layer

Organize `application/` by business feature and operation.

Example:

```text
application/accounts/
    create_account/
        command.py
        handler.py
    get_account/
        query.py
        handler.py
    services/
```

Feature facades export public Commands, Queries, Handlers, and genuinely reused services.

## Commands and Queries

Commands represent state-changing operations.

Queries represent read-only operations.

They are immutable Pydantic values and contain data only.

Do not implement:

- repository access;
- business orchestration;
- fingerprint calculation;
- network calls;

inside Commands or Queries.

## Handlers

A Handler owns one application operation.

Naming:

```text
CreateAccountHandler
GetAccountHandler
ReserveHoldHandler
```

Handlers:

- receive explicit constructor dependencies;
- validate business state;
- coordinate repositories and shared services;
- raise typed application errors;
- return ORM entities or structured application results.

Do not create a command bus, mediator framework, generic use-case executor, or giant service.

## Shared services

Keep a service only when behavior is genuinely reused by several operations.

Examples:

- ledger posting;
- reversal;
- balance projection;
- hold capture;
- fingerprinting;
- deterministic locking.

One-operation logic belongs in its Handler.

---

# Dependency Injection

Keep one small shared dependency package for:

- application resources;
- settings;
- transactional database session.

Feature-specific providers live beside feature routers.

Example:

```text
api/routers/accounts/dependencies.py
api/routers/holds/dependencies.py
```

Providers explicitly construct:

- repositories;
- read query adapters;
- shared services;
- Handler.

Avoid a giant global use-case dependency module.

Avoid named `SomethingDep` aliases used only once.

Use direct:

```python
handler: Annotated[GetAccountHandler, Depends(provide_get_account)]
```

All persistence collaborators for one endpoint receive the same `AsyncSession`.

---

# Database Transaction Lifecycle

One parameterized HTTP request owns one PostgreSQL transaction.

Use:

```python
async def get_database_session(...) -> AsyncIterator[AsyncSession]:
    async with session_factory.begin() as session:
        yield session
```

The FastAPI yield dependency uses function scope:

```python
Depends(get_database_session, scope="function")
```

Lifecycle:

```text
create session
-> BEGIN
-> Handler / services / repositories / queries
-> dependency exits
   -> COMMIT on success
   -> ROLLBACK on exception
-> close session
-> send response
```

Do not manually call:

- `commit()`;
- `rollback()`;
- `begin()`;

inside Handlers, services, repositories, or query adapters.

Do not reintroduce a Unit of Work wrapper around this transaction.

Do not catch and suppress exceptions in the DB dependency.

---

# SQLAlchemy Database Structure

Use one cohesive persistence database package:

```text
persistence/database/
    base.py
    session.py
    mixins/
    models/
    result_readers/
```

## ORM models

- one public ORM model per file;
- SQLAlchemy 2.x typed mappings;
- `Mapped[T]`;
- `mapped_column`;
- typed relationships;
- explicit constraints and indexes;
- meaningful mixins only;
- no Active Record.

ORM classes do not contain:

```text
create
get_by
save
delete
commit
```

Database access belongs to repositories.

## Base and mixins

Keep:

- `Base`;
- standard UUID entity base;
- meaningful `CreatedAtMixin`;
- meaningful timestamp mixin;
- other mixins only when structure is truly repeated.

Do not create inheritance trees merely to remove two columns.

## Relationships

Add typed relationships that simplify real object navigation.

Use explicit loading policy such as:

```text
lazy="raise"
```

to prevent hidden database I/O.

Do not depend on lazy loading during response serialization.

## Database constraints

Critical structural invariants must also be protected by PostgreSQL:

- unique business identifiers;
- operation ID uniqueness;
- foreign keys;
- valid states;
- money sign/range constraints;
- active-resource uniqueness;
- race-sensitive logical uniqueness.

Pydantic validation never replaces DB constraints.

Do not rewrite historical migrations for style.

---

# Repository and Read Query Split

## Entity repositories

`persistence/repositories/` contains entity or aggregate persistence adapters.

Repository reads return:

```text
ORM model
ORM model | None
list[ORM model]
```

Repositories do not return:

- dictionaries indexed by IDs;
- raw Row/RowMapping;
- API responses;
- Pydantic read projections.

If application logic needs an index:

```python
items_by_id = {
    item.id: item
    for item in items
}
```

the application builds it.

## Read query adapters

`persistence/queries/` contains optimized multi-table/aggregate read projections.

Query adapters return typed immutable Pydantic projections.

They do not return raw dictionaries, tuples, or RowMappings.

This is the default CQRS-lite split:

```text
Repository -> ORM entity persistence
Query adapter -> optimized typed read projection
```

Do not call projection readers "Repository".

---

# Base Repositories

Use one small shared execution base:

```text
SQLAlchemyRepository
```

It owns only:

- the request session;
- scalar statement execution;
- projection statement execution.

Use:

```text
SQLAlchemyEntityRepository[T]
```

for normal UUID-ID entities.

It provides common:

```python
async def get_by_id(self, model_id: UUID) -> T | None:
    ...
```

Concrete UUID entity repositories do not repeat identical `get_by_id()`.

Non-standard-key models use semantically correct methods such as `get_by_account_id()`.

The base repository must not become generic CRUD.

It does not own:

- commit/rollback;
- generic create/update/delete;
- filter DSL;
- pagination;
- business rules.

---

# SQLAlchemy Result Readers

All scalar extraction is centralized in:

```text
SQLAlchemyScalarResultReader[T]
```

Public API:

```text
one()
one_or_none()
all()
```

All projection mapping extraction is centralized in:

```text
SQLAlchemyProjectionResultReader[T]
```

Public API:

```text
one()
one_or_none()
all()
```

Concrete repositories and query adapters do not call directly:

```text
scalar()
scalar_one()
scalar_one_or_none()
scalars()
mappings()
tuples()
```

The only approved locations are result-reader implementation modules.

Do not add another result wrapper.

---

# Persistence Writes

Use explicit SQLAlchemy DML:

```text
INSERT
UPDATE
RETURNING
ON CONFLICT
```

Prefer one statement and one result.

Do not use in repository write paths:

```text
AsyncSession.add
add_all
flush
refresh
```

Do not hide:

```text
write -> read -> return reloaded entity
```

inside one method.

A write may return:

- an ORM row from the same `RETURNING`;
- UUID;
- bool;
- affected count;
- `None` on no row/conflict;

when that is the natural persistence outcome.

Repositories never raise generic `RuntimeError` for expected write outcomes. Return an explicit
outcome and let the Handler map it to an application error.

---

# Pagination

Use bounded keyset/cursor pagination for immutable or large histories.

Do not use unbounded lists.

Do not use OFFSET as the production history model.

Centralize:

- cursor structure;
- cursor codec;
- pagination input;
- page result;
- deployment policy;
- repeated timestamp-plus-ID keyset SQL predicate.

Do not build a generic pagination framework.

Each query adapter still owns its:

- columns;
- ordering;
- limit;
- filters.

---

# Errors

Application errors are transport-independent.

Use small semantic categories:

```text
ApplicationError
NotFoundError
ConflictError
InvalidOperationError
IntegrityError
```

Feature errors:

- live in focused feature packages;
- expose stable machine error code;
- expose safe English public message;
- do not import FastAPI status constants.

API error handling is split by category:

```text
application
database
validation
unexpected
```

Central handlers may directly return `JSONResponse`.

Do not create `_json_response` or response factories.

Do not:

- maintain hardcoded SQLSTATE tables;
- parse database exception strings;
- expose SQL, DSNs, constraint names, driver messages, or internal exception strings;
- add `type(exception).__name__` when Logfire already records exception metadata;
- use `del request` to silence lint.

Pass exception objects to Logfire through `_exc_info`.

---

# Enums and Closed Categories

Keep one enum per file under:

```text
domain/enums/
```

Re-export active enums through the package facade.

Use `StrEnum` for closed string categories.

Do not scatter internal magic strings for:

- states;
- operation types;
- reference namespaces;
- source discriminators;
- environments.

Do not write free enum-to-enum normalization helpers inside persistence.

Prefer:

- source-specific discriminated projections;
- native source enums;
- structural ownership by the model that defines the category.

Do not create an enum for arbitrary external/user-provided strings.

---

# Settings

Use one environment-loading root:

```python
class Settings(BaseSettings):
    ...
```

Nested logical groups inherit one shared immutable `SettingsModel`.

Typical groups:

```text
ApplicationSettings
DatabaseSettings
HTTPSettings
PaginationSettings
LogfireSettings
```

Use environment/Pydantic Settings for deployment/runtime values:

- database URL;
- pool and command timeouts;
- pool size;
- environment;
- local HTTP host/port;
- OpenAPI enablement;
- pagination policy;
- Logfire configuration.

Keep true domain invariants in code:

- enum members;
- money bounds;
- state transitions;
- business operation rules.

Do not:

- instantiate Settings at arbitrary module import points;
- scatter `os.getenv`;
- call `load_dotenv()` from application modules;
- print secrets;
- create one huge settings class;
- create a one-field settings class without reason.

Gunicorn worker/process settings belong to deployment/process configuration, not application
Settings.

---

# Observability

Use Pydantic Logfire as the single observability implementation.

Configure once at composition time.

Instrument:

- FastAPI;
- the concrete SQLAlchemy engine.

Do not recreate:

- a custom JSON logger;
- a second OpenTelemetry layer;
- a custom ContextVar logging framework;
- manual exception type metadata.

Telemetry must not capture:

- request bodies by default;
- tokens or credentials;
- cookies;
- DSNs;
- database URLs;
- raw financial or cryptographic payloads;
- secrets.

Use safe identifiers and structured spans/events.

Pass exceptions through `_exc_info`.

---

# Authentication Ownership

The Service Profile must explicitly define authentication ownership.

## Non-auth service

A non-auth service does not issue tokens or own user credentials.

Do not add:

- fake API keys;
- development tokens;
- local scope databases;
- placeholder principals;
- token verification without a defined Auth contract.

A future standard auth token header is a security transport concern and may be added only after the
cross-service contract is explicit.

## Auth service

Only an Auth Service may own:

- credential verification;
- token issuance;
- token refresh;
- revocation;
- scopes/permissions;
- principal identity;
- token introspection or verification contract.

Auth-specific storage, state machines, crypto, and audit rules belong to that service profile.

Do not copy the non-auth prohibition into the Auth Service profile.

---

# Real-Time Services

Use this profile only when `REALTIME_POLICY` requires WebSocket.

Default design:

```text
HTTP RPC -> commands and queries
WebSocket -> snapshots and events
```

Do not use long polling unless it is an explicit fallback requirement.

WebSocket contracts define:

- message type;
- contract version;
- event/message ID;
- operation or command ID when relevant;
- correlation ID;
- stream/resource ID;
- sequence number;
- occurred timestamp;
- typed payload;
- error message;
- reconnect behavior;
- version compatibility.

Use:

```text
snapshot + ordered delta events
```

Clients detect sequence gaps and request/resume from a fresh snapshot or replay.

Do not rely on in-process observers as the public protocol. SDKs may expose typed streams/observer
interfaces over the WebSocket transport.

Do not keep a DB transaction or SQLAlchemy session open for the lifetime of a WebSocket connection.
Create one transaction per command/event operation.

---

# Storage Ownership

Each service owns its database/schema and credentials.

A service:

- does not read or modify another service's tables;
- does not use cross-service foreign keys;
- communicates only through documented API/events;
- validates all external data itself.

Even when several services share one PostgreSQL cluster:

- use separate database users;
- isolate privileges;
- keep schema ownership explicit.

Redis may be used only when the Service Profile defines a concrete responsibility.

Redis must not become a hidden shared database between services.

---

# CLI and Process Model

Use Typer as a small operator/development CLI.

Default command:

```text
<SERVICE_NAME> run
```

It starts one local Uvicorn development worker.

Do not wrap every external tool in Typer.

Production uses Gunicorn with the separate `uvicorn-worker` package:

```text
uvicorn_worker.UvicornWorker
```

Do not use the deprecated `uvicorn.workers.UvicornWorker`.

Production startup is direct Gunicorn, not Typer.

---

# OpenAPI and SDK Contract

OpenAPI is a machine-readable platform contract, not only Swagger documentation.

Every method has:

1. one stable dotted RPC path;
2. one stable explicit `operation_id`;
3. one Request model when input exists;
4. one declared result schema;
5. `ApplicationResponse[T]`;
6. stable error codes.

Design schemas so future Python and Dart SDKs can share the same contract.

A future SDK transport should own centrally:

- base URL;
- timeout;
- JSON serialization;
- envelope parsing;
- stable service errors;
- future auth token forwarding;
- retry policy only where explicitly safe.

Service-specific SDK code should mostly contain:

- Request models;
- result models;
- explicit/generated RPC methods.

Prefer:

```text
FastAPI/Pydantic -> OpenAPI -> generated or validated SDK
```

over manually duplicating schemas forever.

Do not put business logic in SDKs.

---

# Docker

Use a production multi-stage Docker build where useful.

Requirements:

- Python 3.12+;
- deterministic dependency install;
- `PYTHONPATH` configured for `app/`;
- non-root user;
- no `.env`;
- no secrets;
- no development reload;
- no migrations at startup;
- exec-form Gunicorn startup;
- no test dependencies in runtime where avoidable.

Do not combine migration and server startup in one shell command.

---

# Helm and kind

Keep Helm under:

```text
deploy/helm/<service-slug>/
```

Use the lowercase DNS-safe `SERVICE_SLUG` for Kubernetes/Helm technical identifiers.

Use `SERVICE_NAME` in human-facing descriptions and application metadata.

The chart should normally provide:

- Deployment;
- ClusterIP Service;
- ConfigMap for non-secret settings;
- existing Secret references for credentials;
- configurable image repository/tag/pull policy;
- configurable replicas;
- Gunicorn values;
- probes;
- resources;
- pod/container security context;
- kind override values.

Do not:

- commit plaintext secrets;
- add PostgreSQL as a hidden application-chart dependency;
- run migrations automatically on application startup;
- add Auth Service secrets before the contract exists;
- add unused ServiceAccounts/tokens.

Use non-root, dropped capabilities, no privilege escalation, and read-only root filesystem where
the application supports it.

---

# Documentation

Keep concise English documentation covering:

1. service responsibility;
2. source of truth/data ownership;
3. out-of-scope responsibilities;
4. architecture;
5. RPC API convention;
6. Request/ORM Schema/Response boundaries;
7. Command/Query/Handler flow;
8. transaction lifecycle;
9. repositories vs read query adapters;
10. domain invariants;
11. idempotency;
12. settings;
13. observability;
14. authentication ownership;
15. local run;
16. migrations;
17. Docker;
18. Helm/kind;
19. recovery/failure behavior;
20. known limitations.

Split documentation into focused files when README becomes too large.

Do not keep documentation describing removed architecture.

---

# Service-Specific Extension Profiles

Apply only the relevant extension and copy it into the Service Profile.

## Auth Service Extension

The Auth Service owns:

- identities;
- credentials;
- token issuance;
- refresh/revocation;
- scopes and permissions;
- token verification/introspection contract;
- security audit;
- rate limiting policy;
- key rotation/signing configuration.

Do not let other services duplicate this logic.

Define token and permission contracts before implementing adapters in other services.

## Crypto/Custody Service Extension

Use production-grade architecture from the beginning, but blockchain operations remain testnet-only
until an explicit mainnet security stage.

Mandatory:

- PostgreSQL authoritative workflow state;
- no Redis-only withdrawal/deposit truth;
- no mainnet endpoint/chain ID;
- server-owned network configuration;
- persistent deposit/withdrawal state machines;
- idempotent deposit credit and withdrawal submission;
- confirmation handling;
- reorg handling;
- nonce or UTXO management;
- lost-RPC-response recovery;
- private-key boundary;
- no keys in source, API, logs, or ordinary plaintext tables;
- future KMS/HSM/custody adapter seam;
- double-entry internal ledger when the service owns financial balances.

## Poker Server Extension

Use:

```text
HTTP RPC -> commands/queries
WebSocket -> realtime snapshots/events
Redis -> live table state only
PostgreSQL -> durable history/configuration where required
C++ poker engine -> poker rules
Table Actor -> sequential command execution per table
```

Mandatory:

- one sequential command stream per table;
- typed WebSocket event envelope;
- monotonic per-table sequence;
- snapshot on connect/reconnect;
- client gap detection;
- no authoritative money in Redis;
- financial operations through `virtualMoney`;
- Poker Server owns game state, pots, legal actions, timers, and final stack calculation;
- no long polling unless explicit fallback.

---

# Anti-Patterns

Do not add:

```text
Active Record database methods on ORM models
GenericRepository CRUD framework
ResponseFactory / ResponseBuilder
DatabaseReadinessChecker
UnitOfWork over the request transaction dependency
Repository mega-container
global use-case registry
giant dependency alias file
ORM -> identical domain model mapper
raw dict persistence result contracts
dict-indexed ORM collections from repositories
hardcoded SQLSTATE classifications
exception-string parsing
manual enum normalization helpers in repositories
magic internal state/reference strings
fake system/user UUIDs instead of semantic ownership
session.add/flush/refresh repository write flows
hidden read-after-write
mutable global structured configuration
service locator
sys.path mutation
```

---

# Codex Work Mode

By default, Codex should:

- inspect only necessary files;
- make the smallest coherent diff;
- avoid full-repository reformatting;
- avoid expensive verification unless explicitly requested;
- report every assumption and incomplete item honestly.

Do not automatically run:

- tests;
- coverage;
- PostgreSQL;
- Alembic upgrade/downgrade;
- Docker;
- Helm;
- kind;
- deployment.

When a task specifically targets typing or packaging, targeted checks such as the following may be
required:

```bash
uv lock
uv run mypy
python3 -m compileall -q app alembic/env.py
git diff --check
```

Never claim success for a command that was not run.

---

# Tests and CI/CD

Tests and CI/CD are handled separately unless the user explicitly requests them.

Do not add or modify:

- unit tests;
- integration tests;
- E2E tests;
- fixtures;
- coverage;
- pytest configuration;
- GitHub Actions;
- GitLab CI;
- Jenkins;
- CI runners;
- automated deployment pipelines.

The architecture must remain testable:

- dependencies are explicit;
- external systems are behind adapters where they genuinely vary;
- business rules are deterministic where possible;
- time/randomness are injectable when behavior depends on them;
- HTTP is not required to execute application logic.

---

# Completion Report

At the end of a Codex task, report in Russian:

1. what was implemented;
2. architecture decisions;
3. public API changes;
4. migrations;
5. created files;
6. modified files;
7. deleted files;
8. dependency changes;
9. assumptions;
10. known limitations;
11. commands run and exact results;
12. commands intentionally not run;
13. manual verification commands.

Do not call a stage complete when mandatory acceptance criteria remain unfinished.

Do not `git push` unless explicitly requested.

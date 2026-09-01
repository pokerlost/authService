# Persistence and transactions

This page is the canonical ownership contract for PostgreSQL, SQLAlchemy sessions, repositories,
and Alembic in the generated service.

## PostgreSQL ownership

PostgreSQL is the unconditional source of truth for persisted service state. The process owns one
async engine and session factory in application lifespan. A database-consuming request owns one
`AsyncSession`; sessions are not shared between requests.

The database dependency uses SQLAlchemy's transaction context directly:

```python
async with resources.session_factory.begin() as session:
    yield session
```

Normal context exit commits, exceptional exit rolls back, and context completion closes the
session. Routes, application handlers, repositories, and query adapters do not call `begin()`,
`commit()`, or `rollback()`.

## Persistence adapters

Repositories and query adapters receive the request session and execute explicit SQLAlchemy 2
statements. They do not create engines or sessions and do not complete the transaction. ORM
entities, persistence projections, and public API response models remain separate artifacts.

The shared template supplies metadata, repository, result-reader, and projection foundations.
authService adds concrete authorization and OAuth client models only for responsibilities defined
in `SERVICE.md`.

AUTH-02 persists OAuth clients, grant-type permissions, digest-only client credentials, direct
service and client scope grants, and direct service and client audience grants. The audience value
is the exact canonical resource URI; scope and audience tables contain no wildcard or implicit
role-derived machine grant.

The concrete tables are `oauth_clients`, `oauth_client_grant_types`, `oauth_client_secrets`,
`service_scope_grants`, `oauth_client_scope_grants`, `service_audience_grants`, and
`oauth_client_audience_grants`. Their foreign keys retain the existing authorization principal and
scope catalog as explicit security dependencies rather than broad delete cascades.

## Service-client transaction boundaries

`authservice bootstrap-service-client` opens one local session transaction for the service
principal, bound confidential client, grant type, both scope-grant sets, both audience-grant sets,
and active secret digest. A conflict or validation failure rolls the entire bundle back. The CLI
prints the one-time raw secret only after the context exits successfully and commits.

`POST /oauth.token` uses one request-owned transaction for authorization reads. Its query adapter
returns an immutable issuance context rather than ORM entities. The application handler evaluates
the accepted credential records and exact grant intersections, then signs through the
process-owned signer. It does not write or persist the access token.

## Remote calls

Do not hold a PostgreSQL transaction open across a remote `pypokerlost` SDK call. A remote method
call and a local database transaction cannot form one atomic transaction. Structure the application
workflow so remote I/O and a short local persistence phase have explicit ordering and failure
semantics, without treating either side as a distributed commit participant.

The boundary also excludes service-token acquisition, every retry attempt, and every backoff
sleep. Retry is transport recovery, not business reconciliation. A replay-safe mutation must reuse
the same `business_operation_id` and semantic payload against a persisted target idempotency
contract; an ambiguous remote result still requires the owning workflow's reconciliation policy.
authService's current token issuance performs no outbound call.

## Failure mapping

The engine boundary narrowly converts an exact driver `ConnectionRefusedError` into SQLAlchemy's
`OperationalError`. The centralized API handler maps that availability category to a safe `503`
response. Other `SQLAlchemyError` instances become sanitized `500` responses. The request
dependency does not catch or translate these exceptions.

The exact public forms live in `docs/api/errors.md`. The root probe does not open a session or
establish database readiness; see `docs/api/public-surface.md`.

## Alembic metadata

Alembic owns schema migrations against the shared `Base.metadata`. Every concrete ORM model must be
imported through `persistence.database.models` so migration autogeneration can see it. Do not add a
fake baseline model or migration to an otherwise pristine service. The command workflow and review
discipline are documented in
`docs/development/database-migrations.md`.

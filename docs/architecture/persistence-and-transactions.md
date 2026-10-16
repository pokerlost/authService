# Persistence and transactions

PostgreSQL is required for this specialized foundation. The application factory validates `DATABASE_URL` without opening a connection; lifespan owns one async engine and session factory per worker and disposes them on shutdown. Readiness checks the database with a bounded timeout and returns 503 on failure. Liveness does not query it.

## Request boundary

`src/authService/persistence.py` exposes `DatabaseSession` through a function-scoped FastAPI dependency. Its `async_sessionmaker.begin()` commits on success and rolls back on failure before the response is sent. A session belongs to one request task. Future routes, handlers and repositories must not finish this transaction themselves or use lazy ORM loading during response serialization.

Streaming, WebSocket and background work require separate short operations. Do not share an `AsyncSession` across parallel tasks. End any local transaction before SDK calls, token acquisition or retry backoff; a remote call and local database cannot be one atomic transaction.

## Historical revisions

`migrations/versions/` preserves five prior authorization revisions byte-for-byte. The current runtime declares no authorization ORM model and `migrations/env.py` has no autogenerate metadata. A fresh database can still receive old authorization tables if an operator explicitly upgrades the historical chain. Never infer a destructive migration from empty current metadata or change an applied revision. See [migration commands](../development/database-migrations.md).

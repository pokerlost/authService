# Configuration

The application factory reads validated settings when it is called. Importing `authService.app` does not read credentials or connect to PostgreSQL.

## 🧭 Current inputs

| Input | Purpose |
| --- | --- |
| `DATABASE_URL` | Required `postgresql+asyncpg://` DSN for this database-enabled service. Inject it as a process secret. |
| `AUTHSERVICE_LOGLEVEL` | Optional `DEBUG`, `INFO`, `WARNING`, or `ERROR`; default `INFO`. |

The prior flat application accepted `AUTHSERVICE_DATABASE__URL`, pool settings, and mandatory Logfire settings in production. Those names are not read by the new `src/authService/` runtime. Update deployment secrets and environment explicitly; do not assume an automatic alias. `.env.example` is documentation only and is not loaded by the factory. No signing key, client secret, or outbound token is needed for the present infrastructure routes.

Database URL validation happens at factory construction. A connection is opened only by readiness or an enabled database operation; startup never runs Alembic. Liveness does not query the database. See [migration guidance](../development/database-migrations.md) for the separate historical revision graph.

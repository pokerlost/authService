# Architecture overview

The installed `authservice` package contains a FastAPI factory, infrastructure routers, safe Pokerlost errors, a local verifier boundary, typed settings, and process-owned database resources. `SERVICE.md` owns the planned auth data and operation boundary.

## 🧭 Current foundation

`src/authservice/app.py` assembles the application. Lifespan owns one async engine per worker; `/health/live` checks the process and `/health/ready` checks the enabled required database with a timeout. `src/authservice/persistence.py` defines a short request transaction dependency for future HTTP scenarios. No application use case, repository, credential issuer, or business route is registered now.

`src/authservice/scopes.py` is the sole service scope catalog and is currently empty. `src/authservice/authorization.py` requires a real local verifier before any protected route can run. The public OpenAPI path exposes actual registered routes; `pypokerlost` remains the pinned HTTP SDK boundary, not this service's implementation.

`migrations/versions/` retains historical revisions without claiming their old tables as current ORM metadata. Deployment configuration must inject `DATABASE_URL`; no `.env` read, telemetry account, or migration runs at import or startup.

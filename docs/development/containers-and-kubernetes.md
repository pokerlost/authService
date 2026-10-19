# Containers and Kubernetes

The Dockerfile installs the locked `src/authservice/` package and starts the FastAPI factory as a non-root user. It does not copy source credentials or run Alembic on startup. Building the pinned private SDK requires a narrowly scoped GitHub App token passed as a BuildKit `sdk_token` secret; this is a build requirement, not a runtime checkout dependency.

The existing Helm chart uses `uvicorn authservice.app:create_app --factory`, `GET /health/live` and `GET /health/ready`. `DATABASE_URL` is injected from a named Kubernetes Secret; the ConfigMap carries only `AUTHSERVICE_LOGLEVEL`. Removed Logfire, Gunicorn, and nested database settings are not silently accepted. The ClusterIP must be behind trusted HTTPS/TLS termination. Image build, chart rendering, and database readiness need their actual tools and disposable infrastructure before being reported as passed.

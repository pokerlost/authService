# Containers and Kubernetes

The retained Dockerfile builds the `src/authService/` wheel from the lock and starts the FastAPI factory as a non-root user. It does not copy source credentials or run Alembic on startup. Building the private SDK requires authorized Git read access through the existing BuildKit SSH mount; this is a build requirement, not a runtime checkout dependency.

The existing Helm chart uses `uvicorn authService.app:createApp --factory`, `GET /health/live` and `GET /health/ready`. `DATABASE_URL` is injected from a named Kubernetes Secret; the ConfigMap carries only `AUTHSERVICE_LOGLEVEL`. Removed Logfire, Gunicorn, and nested database settings are not silently accepted. The ClusterIP must be behind trusted HTTPS/TLS termination. Image build, chart rendering, and database readiness need their actual tools and disposable infrastructure before being reported as passed.

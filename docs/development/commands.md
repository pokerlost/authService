# Development commands

This page records the current `src/authservice/` foundation commands. Supply `DATABASE_URL` through a private process environment for startup; no local `.env` is loaded automatically.

## 🚀 Run

```bash
uv sync --locked
make run
```

`make run` starts `uvicorn authservice.app:create_app --factory --reload` on loopback. `make serve` runs the same factory without reload; set `HTTP_HOST` and `HTTP_PORT` explicitly for a trusted deployment. No business route or token issuer is started.

## 🛠 Checks

```bash
make lock-check
make format-check
make lint
make typecheck
make compile
make docs-check
make test
uv build
```

`make check` combines the checks above except the build. `make check-full` also runs the existing pre-commit hooks. The infrastructure HTTP suite runs without a database; positive readiness and historical migrations require disposable PostgreSQL. Docker and Helm checks need their actual tools. `make db-upgrade` and `make db-downgrade` are operator actions, never startup steps. `make db-revision message=...` creates only an empty draft.

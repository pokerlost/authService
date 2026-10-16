# Development commands

This page records the current `src/authService/` foundation commands. Supply `DATABASE_URL` through a private process environment for startup; no local `.env` is loaded automatically.

## 🚀 Run

```bash
uv sync --locked
make run
```

`make run` starts `uvicorn authService.app:createApp --factory --reload` on loopback. `make serve` runs the same factory without reload; set `HTTP_HOST` and `HTTP_PORT` explicitly for a trusted deployment. No business route or token issuer is started.

## 🛠 Checks

```bash
make lock-check
make format-check
make lint
make typecheck
make compile
make docs-check
uv build
```

`make check` combines the existing non-test checks above except the build. `make check-full` also runs the existing pre-commit hooks. The repository has no subject test suite; an empty pytest collection is not success. Docker, Helm, and PostgreSQL checks are separate and need their actual infrastructure. `make db-upgrade` and `make db-downgrade` are operator actions, never startup steps. `make db-revision message=...` creates only an empty draft.

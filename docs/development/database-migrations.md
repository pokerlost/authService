# Database migrations

The five historical authService revisions were moved byte-for-byte from `alembic/versions/` to `migrations/versions/`. Their revision IDs and parent graph are unchanged. They can still create older authorization tables on a fresh database even though current runtime metadata has no subject tables. Changing the code foundation does not clear existing storage.

## 🧭 Commands and ownership

`alembic.ini` uses `migrations/`; `migrations/env.py` takes its connection from the installed `authService` package and the required `DATABASE_URL`. The empty foundation has no autogenerate metadata. Inspect history without a database:

```bash
uv run --locked alembic history
```

Only after reviewing a disposable database and the intended revision should an operator run `make db-upgrade`. `make db-revision message=...` creates an empty draft for a separately designed schema change; it does not infer or drop tables. Never run these commands against a live database as part of template update. A release rollback and a schema rollback require separate compatibility decisions.

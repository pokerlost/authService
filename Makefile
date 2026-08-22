.PHONY: install run run-production lint format-check typecheck migration-upgrade migration-create migration-downgrade

install:
	uv sync --locked

run:
	PYTHONPATH=app uv run --locked authservice run

run-production:
	PYTHONPATH=app uv run --locked gunicorn --config gunicorn.conf.py api.asgi:application

lint:
	uv run --locked ruff check .

format-check:
	uv run --locked ruff format --check .

typecheck:
	PYTHONPATH=app uv run --locked mypy

migration-upgrade:
	PYTHONPATH=app uv run --locked alembic upgrade head

migration-create:
	@test -n "$(message)" || (echo "message is required" >&2; exit 2)
	PYTHONPATH=app uv run --locked alembic revision --autogenerate -m "$(message)"

migration-downgrade:
	PYTHONPATH=app uv run --locked alembic downgrade -1

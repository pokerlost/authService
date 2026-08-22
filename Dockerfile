FROM ghcr.io/astral-sh/uv:0.12.5 AS uv

FROM python:3.12-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /service

COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project

COPY app ./app
RUN uv sync --locked --no-dev --no-editable

FROM python:3.12-slim-bookworm AS runtime

ENV PATH=/service/.venv/bin:$PATH \
    PYTHONPATH=/service/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /service

RUN groupadd --gid 10001 authservice \
    && useradd --uid 10001 --gid authservice --no-create-home --shell /usr/sbin/nologin authservice

COPY --from=builder /service/.venv /service/.venv
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini gunicorn.conf.py ./

USER 10001:10001

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "api.asgi:application"]

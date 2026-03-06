# Stage 1: build dependencies with uv
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace root and package sources
COPY pyproject.toml uv.lock ./
COPY packages/raise-core/ packages/raise-core/
COPY packages/raise-server/ packages/raise-server/

# Create venv and install raise-server with all dependencies
RUN uv venv /app/.venv && \
    uv pip install --python /app/.venv/bin/python \
    ./packages/raise-server ./packages/raise-core

# Stage 2: minimal runtime
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy alembic files for migrations
COPY packages/raise-server/alembic/ alembic/
COPY packages/raise-server/alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "raise_server.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

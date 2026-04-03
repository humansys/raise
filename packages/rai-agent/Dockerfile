# rai-agent — multi-stage Docker build
#
# Stage 1: Install Claude Code CLI (Node.js)
# Stage 2: Install rai-agent (Python + uv)
#
# claude-agent-sdk requires the `claude` binary — it spawns it
# as a subprocess via SubprocessCLITransport.
#
# Auth is handled via environment variables. See .env.example for
# all supported scenarios (subscription, API key, Bedrock, Vertex, etc.)
#
# Build from repo root:
#   docker build -f packages/rai-agent/Dockerfile .

# ── Stage 1: Claude Code CLI ─────────────────────────────────────
FROM node:20-slim AS claude-cli
RUN npm install -g @anthropic-ai/claude-code

# ── Stage 2: Python + rai-agent ──────────────────────────────────
FROM python:3.12-slim

# System deps for cryptography and Node.js runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Node.js runtime (required by Claude Code CLI)
COPY --from=claude-cli /usr/local/bin/node /usr/local/bin/node
COPY --from=claude-cli /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/@anthropic-ai/claude-code/cli.js /usr/local/bin/claude \
    && chmod +x /usr/local/bin/claude

# uv for fast Python dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace root config and patch out proprietary package references
# (raise-pro, raise-server are not included in the Docker image)
COPY pyproject.toml uv.lock ./
RUN sed -i '/^raise-server = { workspace = true }/d' pyproject.toml \
    && sed -i '/^raise-pro = { workspace = true }/d' pyproject.toml \
    && sed -i '/^    "raise-pro",$/d' pyproject.toml \
    && sed -i '/^    "raise-server",$/d' pyproject.toml

# Copy workspace packages that rai-agent depends on
COPY packages/raise-core/ packages/raise-core/
COPY packages/raise-cli/ packages/raise-cli/
COPY packages/rai-agent/ packages/rai-agent/

# Install rai-agent and its workspace dependencies
RUN uv sync --package rai-agent --no-dev --frozen

# Default port for the daemon HTTP/WebSocket server
EXPOSE 8000

ENTRYPOINT ["uv", "run", "python", "-m", "rai_agent.daemon"]
CMD ["--host", "0.0.0.0"]

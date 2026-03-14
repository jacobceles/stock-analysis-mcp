# Stage 1: Builder
FROM python:3.14-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files for dependency installation
# We mount the cache for faster builds and avoid copying uv.lock/pyproject.toml if not needed in final image
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime
FROM python:3.14-slim-bookworm AS runtime

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Add the virtual environment's bin to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "stock_analysis_mcp.api.adk_server:app", "--host", "0.0.0.0", "--port", "8080"]

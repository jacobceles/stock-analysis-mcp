# Stage 1: Builder
FROM python:3.14-slim-trixie AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files for dependency installation
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Runtime
FROM python:3.14-slim-trixie AS runtime

# Install system dependencies for Qt6/finplot
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libopengl0 \
    libglib2.0-0 \
    libxkbcommon0 \
    libdbus-1-3 \
    libfontconfig1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxrender1 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

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

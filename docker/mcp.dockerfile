FROM --platform=linux/amd64 python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

EXPOSE 8000

COPY . .

CMD uv run python -m stock_analysis_mcp.server
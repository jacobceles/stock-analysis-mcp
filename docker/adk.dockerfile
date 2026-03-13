FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

EXPOSE 8080

COPY . .

CMD uv run uvicorn stock_analysis_mcp.adk_service:app --host 0.0.0.0 --port 8080
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv
COPY pyproject.toml ./
RUN uv sync

EXPOSE 8080

COPY . .

CMD uv run uvicorn adk_service:app --host 0.0.0.0 --port 8080
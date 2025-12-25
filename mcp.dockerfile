FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv
COPY pyproject.toml ./
RUN uv sync

EXPOSE 8000

COPY . .

CMD uv run python server.py
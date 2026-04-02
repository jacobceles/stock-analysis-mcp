.PHONY: all setup format lint typecheck test docker-build docker-up docker-down docker-logs

all: setup format lint typecheck test

setup:
	uv sync --all-groups
	if [ -d .git ]; then uv run pre-commit install; fi

format:
	uv run ruff format

lint:
	uv run ruff check --fix

typecheck:
	uv run mypy .
	uv run pyrefly check .

test:
	uv run pytest

docker-build:
	docker compose -f docker/compose.yml build

docker-up:
	docker compose -f docker/compose.yml up -d

docker-down:
	docker compose -f docker/compose.yml down

docker-logs:
	docker compose -f docker/compose.yml logs -f

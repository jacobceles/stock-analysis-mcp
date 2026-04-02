.PHONY: all setup format lint typecheck test docker-build docker-up docker-down docker-logs

all: setup format lint typecheck test

setup:
	uv sync --all-groups
	if [ -d .git ]; then \
		if command -v prek >/dev/null 2>&1; then \
			prek install; \
		else \
			echo "WARNING: prek not found. Install it:"; \
			echo "  macOS:         brew install j178/tap/prek"; \
			echo "  Linux/WSL:     curl -fsSL https://raw.githubusercontent.com/j178/prek/main/install.sh | sh"; \
			echo "  Windows/Rust:  cargo install prek"; \
			echo "Git hooks not installed. See README for details."; \
		fi \
	fi

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

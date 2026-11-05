.PHONY: up down run test lint format

up:
	docker compose up -d

down:
	docker compose down

run:
	uv run --env-file .env kybr-pipeline

test:
	uv run pytest --lf -vv

lint:
	uv run ruff check

format:
	uv run ruff check --fix
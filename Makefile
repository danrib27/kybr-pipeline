.PHONY: help up down run test lint format explore
.DEFAULT_GOAL := help

# Arguments of the kybr-pipeline CLI, as in
# make run ARGS="ingest monthly -l compras -i 202402 -f 202404"
ARGS ?=

# Clears the outputs of a notebook read from stdin (git clean filter).
NBSTRIP := uv run --quiet --group explore jupyter nbconvert \
	--to notebook --ClearOutputPreprocessor.enabled=True \
	--stdin --stdout --log-level=ERROR

help: ## show this list of commands
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) \
		| awk -F ':.*## ' '{ printf "  %-8s %s\n", $$1, $$2 }'

up: ## start the services in docker-compose.yml
	docker compose up -d

down: ## stop the services in docker-compose.yml
	docker compose down

run: ## run the CLI with the variables in .env; pass ARGS="..."
	uv run --env-file .env kybr-pipeline $(ARGS)

test: ## run the whole pytest suite
	uv run pytest -vv

lint: ## check the code with Ruff
	uv run ruff check

format: ## apply Ruff's fixes and format the code
	uv run ruff check --fix
	uv run ruff format

explore: ## install Jupyter and strip notebook outputs on git add
	uv sync --group explore
	git config filter.nbstrip.clean '$(NBSTRIP)'
	git config filter.nbstrip.smudge cat
	git config filter.nbstrip.required true

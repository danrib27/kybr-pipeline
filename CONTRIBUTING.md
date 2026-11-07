# Contributing

## Setup

1. Install [uv](https://docs.astral.sh/uv/). It reads the Python
   version (3.12) from `.python-version`.
2. Install the dependencies, dev tools included:

   ```sh
   uv sync
   ```

3. Copy `.env-sample` to `.env` and fill in the variables.
4. Start the local S3 (RustFS) if you don't want to upload to AWS:

   ```sh
   make up
   ```

   Then set `AWS_ENDPOINT_URL=http://localhost:9000` and the RustFS
   keys as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `.env`.
   The web console is at <http://localhost:9001>.

## Everyday commands

| Command | What it does |
| --- | --- |
| `make run` | runs the `kybr-pipeline` CLI with the variables in `.env` |
| `make test` | runs the whole pytest suite |
| `make lint` | checks the code with Ruff |
| `make format` | applies Ruff's fixes and formats the code |
| `make up` / `make down` | starts / stops the services in `docker-compose.yml` |

Dependencies are added with `uv add <package>` (or `uv add --dev`),
never with `pip`.

## Workflow

1. Branch from `main` as `feature/<name>`.
2. Write the code with type hints and Google-style docstrings, in lines
   of at most 79 columns. Each module in `src/kybr_pipeline/` has its
   own `tests/test_<module>.py`.
3. Run `make lint` and `make test` before committing.
4. Record the change in `CHANGELOG.md`, and update `README.md` when what
   the project does or how it is used changes.
5. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
   and open a pull request. CI runs the lint and the tests on it.

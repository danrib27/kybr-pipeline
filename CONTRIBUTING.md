# Contributing

## Setup

1. Install [uv](https://docs.astral.sh/uv/). It reads the Python
   version (3.12) from `.python-version`.
2. Install the dependencies, dev tools included:

   ```sh
   uv sync
   ```

3. Copy `.env.example` to `.env` and fill in the variables.
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
| `make` / `make help` | lists these commands |
| `make run ARGS="..."` | runs the `kybr-pipeline` CLI with the variables in `.env` and the arguments in `ARGS` |
| `make test` | runs the whole pytest suite |
| `make lint` | checks the code with Ruff |
| `make format` | applies Ruff's fixes and formats the code |
| `make up` / `make down` | starts / stops the services in `docker-compose.yml` |

The CLI needs a subcommand, so `make run` takes it in `ARGS`. For
example, to ingest every month of 2021:

```sh
make run ARGS="ingest monthly -l compras -i 202101 -f 202112"
```

Dependencies are added with `uv add <package>` (or `uv add --dev`),
never with `pip`.

## Workflow

1. Branch from `main` as `<type>/<name>`, where the type is the
   Conventional Commits one: `feature/` (for `feat`), `fix/`, `build/`,
   `chore/` or `docs/`. For example, `docs/5-fix-broken-links`.
2. Write the code with type hints and Google-style docstrings, in lines
   of at most 79 columns. Use f-strings, except in logging calls,
   which take `%s` arguments (Ruff G004). Each module in
   `src/kybr_pipeline/` has its own `tests/test_<module>.py`.
3. Run `make lint` and `make test` before committing.
4. Record the change in `CHANGELOG.md`, and update `README.md` when what
   the project does or how it is used changes.
5. Bump the version, following
   [Semantic Versioning](https://semver.org/): `major` for a breaking
   change, `minor` for a new feature, `patch` for a fix or docs.

   ```sh
   uv version --bump minor
   ```

   It updates `pyproject.toml` and `uv.lock`. Then turn
   `## [Unreleased]` in `CHANGELOG.md` into
   `## [<version>] - <YYYY-MM-DD>`, leaving an empty `## [Unreleased]`
   above it.
6. Commit with [Conventional Commits](https://www.conventionalcommits.org/)
   and open a pull request. CI runs the lint and the tests on it, and
   fails if the version is not greater than the one on `main` or has no
   section in `CHANGELOG.md`.

## Good practices

### Test data

Tests and local runs ingest a small sample, never the whole history:

- **Monthly data sets** (`compras`, `licitacoes`): at most one quarter.
  The sample is 2023-T2, the same months for both, so they can be
  joined:

  ```sh
  make run ARGS="ingest monthly -l compras -i 202304 -f 202306"
  make run ARGS="ingest monthly -l licitacoes -i 202304 -f 202306"
  ```

- **Daily data sets** (`ceis`, `cnep`): only one snapshot.
- Ingest one endpoint at a time. The Portal da Transparência sits
  behind a firewall that answers many requests in a row with a CAPTCHA
  (HTTP 405) for some minutes.
- The portal publishes the monthly files months late, and a month not
  published yet answers HTTP 403.

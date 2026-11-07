# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial project structure created with uv: the `kyb_brazil_pipeline`
  package in the src layout, `pyproject.toml` and `.python-version`,
  which pins Python 3.10 for local development.
- `.gitignore` covering Python artifacts, secrets, pipeline data files,
  Terraform state, editor files and the local files of AI coding agents.
- `AGENTS.md` with the project context and the first contribution
  rules for AI coding agents: a 79 column line limit, mandatory
  `CHANGELOG.md` entries, descriptive documentation and local testing
  before every commit.
- `CLAUDE.md` and `GEMINI.md`, which import `AGENTS.md` so that Claude
  Code and Gemini CLI read the same context as the other agents.
- This `CHANGELOG.md`.
- `docker-compose.yml` with the pipeline database: `db` runs
  Postgres 18 and keeps its data in the `postgres_data` volume, and
  `adminer` serves a web UI for it on port 8080. Both share the
  `db_network` network.
- `.env-sample`: the `POSTGRES_USER`, `POSTGRES_PASSWORD` and
  `POSTGRES_DB` variables the `db` service reads from `.env`.
- Ruff lint configuration in `pyproject.toml`: 79 column lines,
  Python 3.12 target and Google-style docstrings. Besides the default
  pycodestyle and Pyflakes rules, it enables isort, naming, pyupgrade,
  bugbear, builtins, comprehensions, simplify, return, pathlib, type
  annotations, timezone-aware datetimes, Bandit security checks,
  pytest style, exception handling, performance and Ruff rules.
  `TRY003` is off, so built-in exceptions may carry their message.
  Tests may use `assert` and skip annotations and docstrings.
- `kybr_pipeline.transfer.download_file`, which streams a file from a URL
  into a directory in chunks and gives up after a timeout, 30 seconds
  by default. The file keeps the name the server gives it, the last
  part of the URL after redirects (such as `202508_Compras.zip`), and
  the function returns its path. The S3 object uses the same name.
- `kybr_pipeline.transfer.upload_2_s3`, which uploads a local file to an
  S3 bucket with the boto3 client. Missing credentials or an S3 error
  raise a `RuntimeError` that keeps the original error as its cause.
  boto3 reads the credentials from `AWS_ACCESS_KEY_ID` and
  `AWS_SECRET_ACCESS_KEY`, which are now listed, empty, in
  `.env-sample`.
- `kybr_pipeline.cli`: the argparse parser and `main`, the
  `kybr-pipeline` entry point, with `-V`/`--version` and two `ingest`
  subcommands. Each one calls its function in `kybr_pipeline.scripts`:
  - `ingest monthly --label <endpoint> [--ref-ini YYYYMM]
    [--ref-fin YYYYMM]`, for `compras` and `licitacoes`.
    `scripts.ingest_monthly` checks that each reference is a real
    month written with six digits, so a typo such as `202413` or
    `20258` fails with a usage error before any download, and
    downloads every month in the range. A missing reference defaults
    to the current month in Belém.
  - `ingest snapshot --label <endpoint>`, for `ceis` and `cnep`. The
    portal keeps only the file of the latest published day, so
    `scripts.ingest_snapshot` takes no reference: it downloads today's
    file and falls back to yesterday's when today's is not out yet.
- `make run`, which runs the `kybr-pipeline` command through
  `uv run --env-file .env`, so the variables in `.env` reach the
  pipeline without an extra dependency. `make test`, `make lint` and
  `make format` also go through `uv run`, so they work without
  activating the virtual environment.
- `kybr_pipeline.configs`, which reads `config.yaml` once, on first
  import, and exposes the settings ready to use: `BASE_URL`,
  `MONTHLY_ENDPOINTS`, `SNAPSHOT_ENDPOINTS`, `CHUNK_SIZE` in bytes,
  `TMP_DIR` as a `Path` and `BUCKET_NAME`. The CLI takes its endpoint
  choices from the endpoint lists, so a new endpoint in `config.yaml`
  needs no code change. The file is `config.yaml` in the current
  directory, or the path in the `KYBR_PIPELINE_CONFIG` environment
  variable.
- `kybr_pipeline.Pipeline`, which uses `kybr_pipeline.configs`. Its
  `ingest` method downloads one Portal da Transparência endpoint for one
  reference and uploads the zip file to S3. Each run uses its own
  temporary directory inside `tmp_dir`, removed at the end, so runs
  in parallel don't overwrite each other's files.
- `docs/README.md`, in English: the index of the project
  documentation. Pages not written yet are marked 🚧.
- pytest in the `dev` dependency group, and the first tests, which run
  without network or AWS access:
  - `tests/test_init.py`: the default behavior of `Pipeline.ingest`,
    with fake `download_file` and `upload_2_s3`. It downloads into a
    new run directory inside `TMP_DIR`, uploads the file to the
    configured bucket under its own name, and removes the run
    directory afterwards, also when the download or the upload fails.
  - `tests/test_scripts.py`: reference validation, the default month
    and the month range of `ingest_monthly`, and the fallback to
    yesterday of `ingest_snapshot` on a 403 or 404. Dates come from a
    frozen clock in the Belém timezone.
  - `tests/test_cli.py`: the subcommands reach the pipeline, and bad
    arguments or references end with a usage error.
  - `tests/test_transfer.py`: `download_file` against a local HTTP
    server, covering the redirect to the zip file, a download in many
    chunks, an HTTP error and the timeout; and `upload_2_s3` with a
    fake `boto3.client`, covering which errors become a `RuntimeError`.
  - `tests/conftest.py`: the fake `Pipeline` that the CLI and scripts
    tests share, and `KYBR_PIPELINE_CONFIG` pointing at the project's
    `config.yaml`, so pytest runs from any directory.
- `.github/workflows/ci.yml`: a GitHub Actions workflow that runs
  on every pull request and every push to `main`. It installs the
  locked dependencies with uv, then runs `ruff check` and pytest. A
  new push cancels the run still going on the same branch.
- `rustfs` service in `docker-compose.yml`: an S3 compatible object
  store for development, with the S3 API on port 9000 and the web
  console on port 9001, keeping its data in the `rustfs_data` volume.
  `rustfs-init` creates the bucket (`S3_BUCKET`, by default the one in
  `config.yaml`) once RustFS answers. Setting `AWS_ENDPOINT_URL`
  points the pipeline at RustFS, since boto3 reads it on its own.
- `.env-sample`: `RUSTFS_ACCESS_KEY`, `RUSTFS_SECRET_KEY`, `S3_BUCKET`
  and a commented `AWS_ENDPOINT_URL` for `make run` against RustFS.

### Changed

- Dates use the `America/Belem` timezone, exported as
  `kybr_pipeline.utils.TIMEZONE`, instead of UTC.
- `AGENTS.md`: condensed and reorganized so agents find each rule
  faster. The documentation rule now asks for clear, succinct and
  descriptive writing that states what each thing does or aims to
  solve, replacing the earlier demand for thorough documentation.
- `README.md`: the project description is wrapped at 79 columns and the
  title is followed by a blank line, to follow the new line length rule
  and the Markdown lint rule that requires blank lines around headings.

### Removed

- The `db` (Postgres) and `adminer` services, the `postgres_data`
  volume and the `db_network` network from `docker-compose.yml`, and
  the `POSTGRES_*` variables from `.env-sample`. The marts will be
  Iceberg tables on S3, registered in the Glue Catalog and built by
  dbt through Athena (`dbt-athena`), so the project has no database
  of its own.

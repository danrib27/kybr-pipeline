# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0] - 2026-11-18

### Added

- `infra/`: Terraform for the whole AWS side, replacing the resources
  made by hand in the console. The data bucket (versioning, SSE-S3
  encryption, public access block, the `raw/`, `bronze/`, `silver/`
  and `gold/` prefixes, and a lifecycle rule that expires noncurrent
  versions after 7 days, removes expired delete markers and aborts
  incomplete multipart uploads after 7 days); the Glue databases
  `bronze`, `silver`, `gold`, `dev_silver` and `dev_gold`; the
  `kybr-pipeline` Athena workgroup, with its results in
  `athena-results/`; and a least-privilege IAM policy, attached to the
  `kybr-pipeline` user, limited to that bucket, workgroup and
  databases. The region is the `region` variable.
  ([#9](https://github.com/danrib27/kybr-pipeline/issues/9))
- `infra/bootstrap/`: the versioned, encrypted S3 bucket that holds
  the Terraform state, with S3 native locking (`use_lockfile`).
  ([#9](https://github.com/danrib27/kybr-pipeline/issues/9))
- `CONTRIBUTING.md`: how to provision and destroy the AWS side.
  ([#9](https://github.com/danrib27/kybr-pipeline/issues/9))

## [0.2.2] - 2026-11-14

### Added

- `docs/decisions.md`: ADR-003, RustFS as the local S3, and ADR-004,
  one processing flow on AWS, with Polars for bronze, Athena as the
  only SQL engine for dbt and DuckDB only for ad-hoc exploration.
  ([#8](https://github.com/danrib27/kybr-pipeline/issues/8),
  [8b87564](https://github.com/danrib27/kybr-pipeline/commit/8b875649e2deaa410437c86c7155f29870400ad9))
- `README.md`: a "Deploying to production" section on running the
  same DAGs on Amazon MWAA, and the limitation of the local Airflow.
  ([#8](https://github.com/danrib27/kybr-pipeline/issues/8),
  [8b87564](https://github.com/danrib27/kybr-pipeline/commit/8b875649e2deaa410437c86c7155f29870400ad9))
- `CONTRIBUTING.md`: a "Good practices" section with the test data
  rule: at most one quarter of the monthly data sets (2023-T2) and one
  snapshot of the daily ones, ingesting one endpoint at a time.
  ([#7](https://github.com/danrib27/kybr-pipeline/issues/7),
  [43d98e2](https://github.com/danrib27/kybr-pipeline/commit/43d98e23b91e20d5d8bf6649956be61060e54fc0))

- `AGENTS.md`, `CONTRIBUTING.md` and `docs/decisions.md`: a published
  ADR is never changed or removed, except for small fixes that keep its
  original meaning; a new decision gets a new ADR.
  ([#8](https://github.com/danrib27/kybr-pipeline/issues/8),
  [ddbd95b](https://github.com/danrib27/kybr-pipeline/commit/ddbd95b9838b48d78ea8fe06790e39962749a1d8))

### Changed

- ADR-002 now says why Dagster was replaced, lists the alternatives
  (Dagster, MWAA, Step Functions), records that Airflow runs locally
  while the data lives on AWS, and uses Airflow 3's
  `airflow backfill create`.
  ([#8](https://github.com/danrib27/kybr-pipeline/issues/8),
  [8b87564](https://github.com/danrib27/kybr-pipeline/commit/8b875649e2deaa410437c86c7155f29870400ad9))
- `AGENTS.md` and `CONTRIBUTING.md`: f-strings everywhere except in
  logging calls, which take `%s` arguments (Ruff G004).
  ([#8](https://github.com/danrib27/kybr-pipeline/issues/8),
  [8b87564](https://github.com/danrib27/kybr-pipeline/commit/8b875649e2deaa410437c86c7155f29870400ad9))
- `README.md`: the roadmap names Polars for bronze and Athena for dbt,
  as in ADR-004.
  ([#8](https://github.com/danrib27/kybr-pipeline/issues/8),
  [8b87564](https://github.com/danrib27/kybr-pipeline/commit/8b875649e2deaa410437c86c7155f29870400ad9))
- `README.md`: the roadmap marks the test sample in `raw/` as done,
  instead of the full backfill of the history.
  ([#7](https://github.com/danrib27/kybr-pipeline/issues/7),
  [43d98e2](https://github.com/danrib27/kybr-pipeline/commit/43d98e23b91e20d5d8bf6649956be61060e54fc0))

## [0.2.1] - 2026-11-14

### Added

- `kybr_pipeline.logs`, with the logging settings and
  `configure_logging`, called once in `cli.main`. The `kybr_pipeline`
  loggers log at the level in `LOG_LEVEL` (INFO by default), or at
  DEBUG with the new `-v`/`--verbose` flag. Other libraries log only
  warnings. An unknown `LOG_LEVEL` is a usage error.
  ([#4](https://github.com/danrib27/kybr-pipeline/issues/4),
  [7eba53d](https://github.com/danrib27/kybr-pipeline/commit/7eba53dc182997ef63c14bc980013671df0df5e1))
- `Pipeline.ingest` logs one INFO line per reference with the URL, the
  file name and size, the S3 object and the elapsed time, so a
  backfill shows one line per month. At DEBUG, `download_file`,
  `upload_2_s3` and the end of the download are logged too.
  ([#4](https://github.com/danrib27/kybr-pipeline/issues/4),
  [7eba53d](https://github.com/danrib27/kybr-pipeline/commit/7eba53dc182997ef63c14bc980013671df0df5e1))
- `ingest monthly` logs the range before it starts and the month that
  fails, and `ingest snapshot` warns when it falls back to yesterday.
  ([#4](https://github.com/danrib27/kybr-pipeline/issues/4),
  [7eba53d](https://github.com/danrib27/kybr-pipeline/commit/7eba53dc182997ef63c14bc980013671df0df5e1))
- Tests of the log messages with `caplog`, and `tests/test_logs.py`
  for the log level set by `LOG_LEVEL` and `--verbose`.
  ([#4](https://github.com/danrib27/kybr-pipeline/issues/4),
  [7eba53d](https://github.com/danrib27/kybr-pipeline/commit/7eba53dc182997ef63c14bc980013671df0df5e1))
- `README.md`: a Roadmap section, which the status note already linked
  to, with what is done and the planned work linked to its issues.
  ([#5](https://github.com/danrib27/kybr-pipeline/issues/5),
  [8930804](https://github.com/danrib27/kybr-pipeline/commit/893080475445c9d79ac1f18dc90e50a45003bc5f))
- `Version bump` CI job: a pull request fails if the version in
  `pyproject.toml` is not greater than the base branch's, or has no
  section in `CHANGELOG.md`.
  ([#6](https://github.com/danrib27/kybr-pipeline/issues/6),
  [bd1860a](https://github.com/danrib27/kybr-pipeline/commit/bd1860abd46104a3791889a0b94f1e39c3d9fba5))
- `make help`, the default goal, lists the `make` targets with a
  one-line description each.
  ([#6](https://github.com/danrib27/kybr-pipeline/issues/6),
  [eda4faa](https://github.com/danrib27/kybr-pipeline/commit/eda4faad5f13314c429e1c38ff881eb98640fa32))

### Changed

- `README.md`: the Tech stack lists only what the code uses today; the
  planned tools (Glue, Athena, Iceberg, DuckDB / Polars, dbt, Airflow,
  Terraform) moved to the Roadmap.
  ([#5](https://github.com/danrib27/kybr-pipeline/issues/5),
  [8930804](https://github.com/danrib27/kybr-pipeline/commit/893080475445c9d79ac1f18dc90e50a45003bc5f))
- `docs/README.md` links only to pages that exist. The others will be
  added when they are written.
  ([#5](https://github.com/danrib27/kybr-pipeline/issues/5),
  [8930804](https://github.com/danrib27/kybr-pipeline/commit/893080475445c9d79ac1f18dc90e50a45003bc5f))
- Branches are named `<type>/<name>` after the Conventional Commits
  type (`feature/`, `fix/`, `chore/`, `docs/`), in `CONTRIBUTING.md`
  and `AGENTS.md`.
  ([#5](https://github.com/danrib27/kybr-pipeline/issues/5),
  [8930804](https://github.com/danrib27/kybr-pipeline/commit/893080475445c9d79ac1f18dc90e50a45003bc5f))
- `.env-sample` renamed to `.env.example`, matching the exception in
  `.gitignore`.
  ([#5](https://github.com/danrib27/kybr-pipeline/issues/5),
  [8930804](https://github.com/danrib27/kybr-pipeline/commit/893080475445c9d79ac1f18dc90e50a45003bc5f))
- `make run` passes the `ARGS` variable to the CLI, as in
  `make run ARGS="ingest monthly -l compras -i 202101 -f 202112"`, since
  the CLI needs a subcommand. Both are documented in `CONTRIBUTING.md`.
  ([#6](https://github.com/danrib27/kybr-pipeline/issues/6),
  [eda4faa](https://github.com/danrib27/kybr-pipeline/commit/eda4faad5f13314c429e1c38ff881eb98640fa32))
- `build/` joins the branch types in `AGENTS.md` and
  `CONTRIBUTING.md`, for build system changes such as the `Makefile`.
  ([#6](https://github.com/danrib27/kybr-pipeline/issues/6),
  [eda4faa](https://github.com/danrib27/kybr-pipeline/commit/eda4faad5f13314c429e1c38ff881eb98640fa32))
- Every pull request bumps the version with `uv version --bump` and
  gives it a section in `CHANGELOG.md`, in `AGENTS.md` and
  `CONTRIBUTING.md`.
  ([#6](https://github.com/danrib27/kybr-pipeline/issues/6),
  [bd1860a](https://github.com/danrib27/kybr-pipeline/commit/bd1860abd46104a3791889a0b94f1e39c3d9fba5))
- Version bumped to 0.2.1.

## [0.2.0] - 2026-11-09

### Added

- `kybr_pipeline.transfer.retry_session`, a `requests.Session` with an
  `HTTPAdapter` and a `urllib3` `Retry`. It retries connection errors,
  timeouts and the 429, 500, 502, 503 and 504 status in
  `transfer.RETRY_STATUS`, with exponential backoff, and honors the
  `Retry-After` header. 403 and 404 are not retried, so
  `ingest snapshot` still falls back to yesterday at once.
  ([#3](https://github.com/danrib27/kybr-pipeline/issues/3))
- `tests/test_transfer.py`: `/flaky/<status>` and `/down/<status>`
  routes in the fake portal, and tests that a route failing twice,
  then answering, is downloaded; that 403 and 404 get a single
  request; and that an error that persists raises `requests.HTTPError`
  after the last retry.
  ([#3](https://github.com/danrib27/kybr-pipeline/issues/3))

### Changed

- `download_file` goes through `retry_session`, so a transient portal
  error no longer aborts a backfill. The new `retries` (5 by default)
  and `backoff_factor` (1 second by default) arguments tune it. A
  timeout that persists after the retries now raises
  `requests.ConnectionError` instead of `requests.Timeout`.
  ([#3](https://github.com/danrib27/kybr-pipeline/issues/3))
- Version bumped to 0.2.0.

## [0.1.0]

### Added

- Initial project structure created with uv: the `kybr_pipeline`
  package in the src layout, `pyproject.toml` and `.python-version`,
  which pins Python 3.12 for local development.
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

- `CONTRIBUTING.md`: setup with uv and the local RustFS, the `make`
  targets and the branch, test, changelog and commit workflow.
- `docs/decisions.md`: ADR-002, which moves the orchestration from
  Dagster to Airflow. DAG runs per data interval track the processed
  batches and `airflow dags backfill` replaces Dagster partitions.
- `.gitignore`: dbt seeds (`dbt/seeds/**/*.csv`) stay versioned,
  although other CSV files are ignored.
- `AWS_REGION` in `.env-sample`.

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

- `requires-python` is now `>=3.12`, matching `.python-version` and
  the Ruff target. `uv.lock` dropped the `tomli` and
  `typing-extensions` backports that only Python 3.10 and 3.11 needed.
- `upload_2_s3` no longer pins `us-east-1`: boto3 reads the region from
  `AWS_REGION`, as it reads `AWS_ENDPOINT_URL`.
- `make test` runs the whole suite instead of only the tests that
  failed last time (`--lf`), and `make format` now also runs
  `ruff format` after `ruff check --fix`.
- `README.md` lists Airflow instead of Dagster in the tech stack.
- The code and the tests are formatted with `ruff format`: double
  quotes and its line wrapping.
- `docs/README.md`: the Docker item now refers to the local RustFS,
  and Data Modeling (`data-model.md`) covers the raw, bronze and gold
  layers and the dbt marts instead of ER diagrams.
- `AGENTS.md`: the entry point is `kybr_pipeline.cli:main`.
- `test_init.py` expects the S3 key under `raw/<endpoint>/`, the
  naming that `Pipeline.ingest` uses since the upload fix.

### Removed

- The `db` (Postgres) and `adminer` services, the `postgres_data`
  volume and the `db_network` network from `docker-compose.yml`, and
  the `POSTGRES_*` variables from `.env-sample`. The marts will be
  Iceberg tables on S3, registered in the Glue Catalog and built by
  dbt through Athena (`dbt-athena`), so the project has no database
  of its own.
- The empty `Pipeline.etl` method: dbt builds the tables through
  Athena, so the package only ingests.
- The Pydantic rule from `AGENTS.md`: the project has no API or
  request bodies.
- The API Specification and Code of Conduct items from
  `docs/README.md`.

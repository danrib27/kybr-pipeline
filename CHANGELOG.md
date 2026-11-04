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
- `kybr_pipeline.ingest.download_file`, which streams a file from a URL
  into a directory in chunks and gives up after a timeout, 30 seconds
  by default. The file keeps the name the server gives it, the last
  part of the URL after redirects (such as `202508_Compras.zip`), and
  the function returns its path. The S3 object uses the same name.
- `kybr_pipeline.ingest.upload_2_s3`, which uploads a local file to an
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
    month, so a typo fails with a usage error before any download, and
    downloads every month in the range. A missing reference defaults
    to the current month in Belém.
  - `ingest snapshot --label <endpoint>`, for `ceis` and `cnep`. The
    portal keeps only the file of the latest published day, so
    `scripts.ingest_snapshot` takes no reference: it downloads today's
    file and falls back to yesterday's when today's is not out yet.
- `kybr_pipeline.configs`, which reads `config.yaml` once, on first
  import, and exposes the settings ready to use: `BASE_URL`,
  `MONTHLY_ENDPOINTS`, `SNAPSHOT_ENDPOINTS`, `CHUNK_SIZE` in bytes,
  `TMP_DIR` as a `Path` and `BUCKET_NAME`. The CLI takes its endpoint
  choices from the endpoint lists, so a new endpoint in `config.yaml`
  needs no code change.
- `kybr_pipeline.Pipeline`, which uses `kybr_pipeline.configs`. Its
  `ingest` method downloads one Portal da Transparência endpoint for one
  reference and uploads the zip file to S3. Each run uses its own
  temporary directory inside `tmp_dir`, removed at the end, so the
  runs Airflow starts in parallel don't overwrite each other's files.
- `docs/README.md`, in English: the index of the project
  documentation. Pages not written yet are marked 🚧.

### Changed

- `README.md`: the project description is wrapped at 79 columns and the
  title is followed by a blank line, to follow the new line length rule
  and the Markdown lint rule that requires blank lines around headings.

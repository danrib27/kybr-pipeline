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

## AWS infrastructure

The AWS side lives in `infra/` as Terraform (1.10 or newer), in two
stacks. It needs credentials of an admin, not the pipeline's.

Bucket names are unique across AWS. If a bucket with the name of the
state or the data bucket already exists outside Terraform, delete it,
or bring it in with an `import` block, before the first `apply`.

1. Once per account, create the bucket that holds the Terraform state.
   Its own state stays local, in `infra/bootstrap/`:

   ```sh
   terraform -chdir=infra/bootstrap init
   terraform -chdir=infra/bootstrap apply
   ```

2. Create the data bucket, the Glue databases, the Athena workgroup
   and the pipeline's IAM user and policy:

   ```sh
   terraform -chdir=infra init
   terraform -chdir=infra apply
   ```

3. Create an access key for the `kybr-pipeline` user and put it in
   `.env`. It is made outside Terraform so the secret never lands in
   the state:

   ```sh
   aws iam create-access-key --user-name kybr-pipeline
   ```

The region is the `region` variable (`us-east-1` by default). The
backend in `infra/terraform.tf` cannot read variables, so a new region
also goes there and in `infra/bootstrap`.

`terraform destroy` refuses to delete a data bucket that has objects.
To rebuild everything, apply `force_destroy` first, which also deletes
the data:

```sh
terraform -chdir=infra apply -var force_destroy=true
terraform -chdir=infra destroy -var force_destroy=true
```

Before a pull request, run `terraform fmt -recursive infra` and
`terraform validate` in each stack. CI runs both on every pull
request, without AWS credentials.

## Everyday commands

| Command | What it does |
| --- | --- |
| `make` / `make help` | lists these commands |
| `make run ARGS="..."` | runs the `kybr-pipeline` CLI with the variables in `.env` and the arguments in `ARGS` |
| `make test` | runs the whole pytest suite |
| `make lint` | checks the code with Ruff |
| `make format` | applies Ruff's fixes and formats the code |
| `make up` / `make down` | starts / stops the services in `docker-compose.yml` |
| `make explore` | installs Jupyter and Polars and strips notebook outputs on `git add` |

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

### Notebooks

Data exploration lives in Jupyter notebooks in `notebooks/`, with the
`explore` dependency group (Jupyter and Polars). Run once per clone:

```sh
make explore
```

It installs the group and sets up the `nbstrip` git filter, which
`.gitattributes` applies to every `.ipynb`: `git add` stores the
notebook without its outputs, while the file on disk keeps them. The
outputs hold samples of the data, which stays out of git. CI fails a
pull request with a notebook that has outputs.

What a notebook finds about a data set goes into its page of the
[data dictionary](docs/data/README.md).

### Architecture decision records

A published ADR in [`docs/decisions.md`](docs/decisions.md) is never
changed or removed, except for small fixes (typos, links, wording) that
keep its original meaning. A new or reversed decision gets a new ADR,
which amends or supersedes the old one, and the old ADR only gets its
status updated, as in "Accepted; amended by ADR-002".

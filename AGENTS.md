# AGENTS.md

## Project Setup and Management

- Python version: 3.12. Don't use newer syntax.
- Dependency management: `uv` and `pyproject.toml`. Never use `pip`
  or a `requirements.txt` file.
- Add a dependency with `uv add <package>`. Never use `uv pip`
  for dependencies.
- Run the app with `make run`.
- Branch from `main` as `<type>/<name>`, with the Conventional Commits
  type: `feature/` (for `feat`), `fix/`, `chore/` or `docs/`. Use
  Conventional Commits.
- Stage changes for review. Don't commit to `main` or push without
  being asked.
- Don't create, install or remove new packages or new files without being
asked.

## Coding Conventions

- Line length at most 79 columns.
- Type-hint public functions and methods, including their return types. Don't
use `return None`.
- Use `pathlib` for path management. Don't use `os.path`.
- Prefer f-strings over `str.format()` or `%` formatting.
- Follow EAFP: handle exceptions rather than checking conditions up front.
- Write Google-style docstrings for every public function and method.
- Embrace idiomatic Python like comprehensions, generators, and decorators.

## Project Structure

- Don't create, install, remove packages or files without being asked.
- `src/kybr_pipeline/`: Python package (src layout, `uv_build`).
  The `kybr-pipeline` command runs `kybr_pipeline.cli:main`.
- `tests/`: automated tests. Each module in `src/kybr_pipeline/` have your own
test file with `test_*.py` prefix.
- `infra/`: infrastructure as code.
- `docs/`: project documentation.

## Documentation update

- All new changes must be documented in `CHANGELOG.md`. When applied, link the
commit and issue id.
- Update `CONTRIBUTING.md` when setup, workflow or these rules change.
- Update `README.md` when what the project does, or how it is installed
and used, changes.
- Update `schemas.yml` (dbt) when a model, column or test is added,
removed or altered.

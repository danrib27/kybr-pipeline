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
- `docs/README.md`, in English: the index of the project
  documentation. Pages not written yet are marked 🚧.

### Changed

- `README.md`: the project description is wrapped at 79 columns and the
  title is followed by a blank line, to follow the new line length rule
  and the Markdown lint rule that requires blank lines around headings.

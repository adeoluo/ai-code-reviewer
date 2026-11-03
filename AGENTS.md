# AGENTS.md

Working notes for coding agents and contributors in **AI Code Reviewer**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

An automated code reviewer powered by a plugged-in language model, with an evaluation harness that measures bug-catching precision and recall on a labeled benchmark of bug-introducing diffs.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/ai_code_reviewer/__init__.py`: AI Code Reviewer - automated code review with a bug-catching benchmark.
- `src/ai_code_reviewer/cli.py`: Command line interface for the code reviewer.
- `src/ai_code_reviewer/data.py`: A labeled benchmark of diffs, each marked as introducing a bug or clean.
- `src/ai_code_reviewer/diff.py`: A minimal unified-diff parser.
- `src/ai_code_reviewer/evaluation.py`: Evaluation: line-level precision and recall of catching planted bugs.
- `src/ai_code_reviewer/observability.py`: In-process request metrics for the HTTP service (Prometheus text exposition).
- `src/ai_code_reviewer/provider.py`: The language-model provider interface, a deterministic fake, and a real client.
- `src/ai_code_reviewer/reviewer.py`: The reviewer: build a prompt from a diff, call the provider, parse comments.
- `src/ai_code_reviewer/rules.py`: A rule-based bug detector over added diff lines.
- `src/ai_code_reviewer/service.py`: A standard-library HTTP service exposing the code reviewer.

## Commands

| Command | Purpose |
|---|---|
| `make help` | Show this help |
| `make setup` | Install dependencies and pre-commit hooks |
| `make format` | Format automatically |
| `make lint` | Lint (no fixes) |
| `make type` | Type-check |
| `make test` | Run tests |
| `make coverage` | Tests with coverage gate |
| `make evaluation` | Reproduce the results table |
| `make run` | Run the HTTP service |
| `make diagram` | Render architecture diagram to SVG |
| `make docker-build` | Build the image |
| `make docker-up` | Run via docker compose |
| `make clean` | Remove caches and artifacts |
| `make all` | Full local gate (mirror of continuous integration) |
| `make changelog` | Regenerate CHANGELOG.md from Conventional Commits (git-cliff) |
| `make cut-release` | Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional) |

Run the full local gate (`make all`) before committing; CI runs the same checks.

## Conventions

- Commits follow Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`).
  The changelog and the next version number are derived from them.
- Every number quoted in the README is produced by a command in this repository. When behavior
  changes, rerun that command and update the number in the same commit.
- When a component is added, removed or renamed, update `docs/architecture/architecture.mmd`
  and re-render `architecture.svg` so the diagram matches the code.
- README sections keep their fixed order. Prose avoids em and en dashes and promotional wording.
- Tests accompany behavior changes; a bug fix comes with a test that fails without it.
- Releases are cut with `make cut-release`.

## Python notes

- Python is managed with `uv`; run commands through `uv run` so the locked environment is used.
- Lint and format with `ruff`; type-check with `mypy`; tests use `pytest`.
- Public functions carry type hints and a docstring that states the contract, not the steps.

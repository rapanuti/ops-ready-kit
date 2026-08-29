# AGENTS.md

## Architecture
- Python package in `src/ops_ready_kit`.
- CLI entrypoint: `ops-ready-kit` using Typer.
- Scanner builds a structured project diagnosis.
- Generators render Markdown, HTML, and deployment artifacts from that diagnosis.

## Development Commands
- Install: `python -m pip install -e ".[dev]"`
- Run CLI: `ops-ready-kit analyze . --output ops-ready-output`
- Tests: `pytest`
- Lint: `ruff check .`
- Format: `ruff format .`
- Types: `mypy src`

## Conventions
- Python 3.12+.
- Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`.
- Keep generated operational docs deterministic and reviewable.
- Prefer small features with focused tests.

## Git Flow
1. Create or select a real issue.
2. Create a branch named `codex/<short-topic>`.
3. Implement, test, lint, type-check, and document.
4. Commit and push.
5. Open a PR and wait for CI.
6. Fix failures before merge.
7. Merge only green PRs, then delete the branch and close the issue.

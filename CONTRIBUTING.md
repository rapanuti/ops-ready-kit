# Contributing

Thanks for helping make ops-ready-kit useful for real teams.

## Local Setup

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

## Workflow

1. Pick or create an issue that describes a real improvement.
2. Create a focused branch.
3. Add tests for behavior changes.
4. Update documentation when user-facing output changes.
5. Open a pull request with a clear summary and test evidence.

## Quality Bar

- Generated output should be deterministic.
- Findings should be actionable, not noisy.
- Avoid credentials, secrets, or private data in fixtures.
- Do not create empty commits, empty issues, or artificial activity.

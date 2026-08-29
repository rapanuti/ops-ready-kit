# Local Setup

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

Use `ops-ready-kit analyze . --output ops-ready-output` to test the CLI against this repository.

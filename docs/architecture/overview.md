# Architecture Overview

ops-ready-kit has three core layers:

1. CLI commands in `src/ops_ready_kit/cli.py`.
2. Repository analysis in `src/ops_ready_kit/scanner.py`.
3. Artifact generation in `src/ops_ready_kit/generator.py`.

The scanner returns a Pydantic `ProjectDiagnosis`. Generators consume that model to produce deterministic Markdown, YAML, HTML, and deployment templates.

## Design Goals

- Keep generated files readable in pull requests.
- Prefer actionable findings over broad warnings.
- Preserve a stable diagnosis schema for future integrations.
- Avoid collecting secrets or private repository contents in reports.

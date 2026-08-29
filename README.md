# ops-ready-kit

[![CI](https://github.com/rapanuti/ops-ready-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/rapanuti/ops-ready-kit/actions/workflows/ci.yml)

Generate operational documentation and deployment readiness artifacts from a software repository.

ops-ready-kit helps developers, DevOps engineers, SREs, and system administrators turn repository signals into practical operational material: runbooks, deployment notes, architecture summaries, security checklists, health check guidance, CI templates, and deployment starter files.

## What It Generates

- `RUNBOOK.md`
- `OPERATIONS-N1.md`
- `OPERATIONS-N2.md`
- `ARCHITECTURE.md`
- `DEPLOYMENT.md`
- `SECURITY.md`
- `PRODUCTION-CHECKLIST.md`
- `diagnosis.yaml`
- `report.html`
- Optional Dockerfile, Docker Compose, Kubernetes, GitHub Actions, and health check templates

## Install

```bash
python -m pip install ops-ready-kit
```

For local development:

```bash
python -m pip install -e ".[dev]"
```

## Quick Start

```bash
ops-ready-kit analyze /path/to/repository --output ops-ready-output
```

Then review the generated files in `ops-ready-output/`.

## Example

```bash
ops-ready-kit analyze examples/python-fastapi --output /tmp/ops-report
```

Output:

```text
RUNBOOK.md
OPERATIONS-N1.md
OPERATIONS-N2.md
ARCHITECTURE.md
DEPLOYMENT.md
SECURITY.md
PRODUCTION-CHECKLIST.md
diagnosis.yaml
report.html
```

## Current Detectors

- Python, JavaScript/TypeScript, Go, Rust, Ruby, and Java signals
- Django, FastAPI, Flask, React, Next.js, Vue, and Express hints
- Dockerfile and Docker Compose
- Kubernetes manifests
- GitHub Actions workflows
- Health, readiness, and liveness hints
- Security policy and dependency scanning files

## Development

```bash
pytest
ruff check .
ruff format .
mypy src
```

## Project Status

The project is in early alpha. The generated files are intentionally conservative and should be reviewed before production use.

## Community Principles

This project does not use artificial GitHub activity. Issues, pull requests, discussions, and releases should represent real work.

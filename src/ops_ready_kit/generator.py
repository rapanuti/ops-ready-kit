from __future__ import annotations

import html
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined

from ops_ready_kit.models import GeneratedArtifact, ProjectDiagnosis

ENV = Environment(autoescape=False, trim_blocks=True, lstrip_blocks=True, undefined=StrictUndefined)


def generate_all(
    diagnosis: ProjectDiagnosis,
    output_dir: Path,
    *,
    include_deployment_templates: bool = True,
) -> list[GeneratedArtifact]:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = [
        _write(output_dir / "RUNBOOK.md", _render_runbook(diagnosis), "operator runbook"),
        _write(output_dir / "OPERATIONS-N1.md", _render_n1(diagnosis), "N1 operations guide"),
        _write(output_dir / "OPERATIONS-N2.md", _render_n2(diagnosis), "N2 operations guide"),
        _write(
            output_dir / "ARCHITECTURE.md", _render_architecture(diagnosis), "architecture report"
        ),
        _write(output_dir / "DEPLOYMENT.md", _render_deployment(diagnosis), "deployment guide"),
        _write(output_dir / "SECURITY.md", _render_security(diagnosis), "security report"),
        _write(
            output_dir / "PRODUCTION-CHECKLIST.md",
            _render_checklist(diagnosis),
            "production checklist",
        ),
        _write(
            output_dir / "diagnosis.yaml", _render_yaml(diagnosis), "machine-readable diagnosis"
        ),
        _write(output_dir / "report.html", _render_html(diagnosis), "HTML report"),
    ]
    if include_deployment_templates:
        artifacts.extend(_deployment_templates(diagnosis, output_dir))
    return artifacts


def _write(path: Path, content: str, description: str) -> GeneratedArtifact:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return GeneratedArtifact(path=path, description=description)


def _render_runbook(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """# {{ d.name }} Runbook

## Service Summary

{% set docker_ports = d.dockerfile.exposed_ports if d.dockerfile else [] -%}
- Primary language: {{ d.primary_language }}
- Frameworks: {{ d.frameworks | join(", ") if d.frameworks else "none detected" }}
- Package managers: {{ d.package_managers | join(", ") if d.package_managers else "none detected" }}
- Docker: {{ "yes" if d.docker else "no" }}
- Docker base images: {{ d.dockerfile.base_images | join(", ") if d.dockerfile else "none" }}
- Docker exposed ports: {{ docker_ports | join(", ") if docker_ports else "none detected" }}
- Kubernetes: {{ "yes" if d.kubernetes else "no" }}
- CI: {{ "GitHub Actions" if d.github_actions else "not detected" }}

## Standard Checks

1. Confirm the latest deployment version.
2. Review recent commits, releases, and incidents.
3. Check service health endpoints and dependency status.
4. Inspect logs for error spikes.
5. Validate rollback instructions before making changes.

## Health Checks

{% if d.health_checks -%}
Health check signals were detected in the repository.
Confirm exact endpoint paths before production use.
{% else -%}
No obvious health check endpoint was detected.
Add `/health`, `/ready`, and `/live` endpoints or equivalent probes.
{% endif %}

## Escalation

- N1: Follow documented checks and collect evidence.
- N2: Diagnose code, infrastructure, and deployment failures.
- Maintainer: Approve production changes and releases.

## Generated Recommendations

{% for item in d.recommendations -%}
- {{ item }}
{% else -%}
- No immediate recommendations.
{% endfor %}
""",
        diagnosis,
    )


def _render_n1(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """# {{ d.name }} N1 Operations

## Goal

Help first-line responders identify common failure signals and gather enough context for escalation.

## Triage Checklist

- Is the service reachable?
- Are health checks passing?
- Did a deployment happen recently?
- Are logs showing repeated errors?
- Are external dependencies unavailable?

## Evidence to Capture

- Timestamp and timezone.
- User-visible impact.
- Latest deployment or commit.
- Error messages and request IDs.
- Screenshots or links to dashboards where available.

## Escalate to N2 When

- Impact is production-facing.
- Rollback or infrastructure changes may be required.
- The same alert repeats after standard remediation.
""",
        diagnosis,
    )


def _render_n2(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """# {{ d.name }} N2 Operations

## Diagnostic Areas

- Application runtime: {{ d.primary_language }}
- Frameworks: {{ d.frameworks | join(", ") if d.frameworks else "none detected" }}
- Build and package managers:
  {{ d.package_managers | join(", ") if d.package_managers else "none detected" }}
- Deployment files: {{ d.deployment_files | length }}

## Deep Checks

1. Reproduce the failing path in a controlled environment.
2. Compare configuration between last known good and current deployment.
3. Review CI output and artifact provenance.
4. Check dependency, database, queue, and network failures.
5. Prepare rollback or forward fix with explicit validation steps.

## Known Gaps

{% for warning in d.warnings -%}
- {{ warning }}
{% else -%}
- No generated warnings.
{% endfor %}
""",
        diagnosis,
    )


def _render_architecture(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """# {{ d.name }} Architecture

## Detected Stack

- Languages: {{ d.languages | join(", ") if d.languages else "unknown" }}
- Frameworks: {{ d.frameworks | join(", ") if d.frameworks else "none detected" }}
- Package managers: {{ d.package_managers | join(", ") if d.package_managers else "none detected" }}

## Operational Signals

{% for file in d.notable_files -%}
- `{{ file.path }}`: {{ file.reason }}
{% else -%}
- No standard metadata files detected.
{% endfor %}

## Deployment Surface

{% for file in d.deployment_files -%}
- `{{ file.path }}`: {{ file.reason }}
{% else -%}
- No deployment files detected.
{% endfor %}

{% if d.dockerfile %}
## Dockerfile Summary

- Base images:
  {{ d.dockerfile.base_images | join(", ") if d.dockerfile.base_images else "none detected" }}
- Exposed ports:
  {{ d.dockerfile.exposed_ports | join(", ") if d.dockerfile.exposed_ports else "none detected" }}
- Healthcheck: {{ "yes" if d.dockerfile.has_healthcheck else "no" }}
- Runtime user: {{ d.dockerfile.user or "not set" }}
- Workdir: {{ d.dockerfile.workdir or "not set" }}
- Command: {{ d.dockerfile.command or "not detected" }}
{% endif %}

## Architecture Notes

This report is generated from repository signals.
Treat it as a starting point and update it with runtime topology, data stores,
queues, external APIs, and ownership details.
""",
        diagnosis,
    )


def _render_deployment(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """# {{ d.name }} Deployment

## Current Signals

- Dockerfile: {{ "detected" if d.docker else "not detected" }}
- Docker Compose: {{ "detected" if d.docker_compose else "not detected" }}
- Kubernetes: {{ "detected" if d.kubernetes else "not detected" }}
- GitHub Actions: {{ "detected" if d.github_actions else "not detected" }}

## Recommended Pipeline

1. Install dependencies.
2. Run lint, type checks, and tests.
3. Build the deployable artifact.
4. Run smoke checks.
5. Deploy with a rollback path.
6. Verify health and readiness after deployment.

## Generated Artifact Notes

Generated deployment files are templates.
Review ports, commands, secrets, resources, and registry names before production use.

{% if d.dockerfile %}
## Dockerfile Review

- Base images:
  {{ d.dockerfile.base_images | join(", ") if d.dockerfile.base_images else "none detected" }}
- Exposed ports:
  {{ d.dockerfile.exposed_ports | join(", ") if d.dockerfile.exposed_ports else "none detected" }}
- Healthcheck: {{ "present" if d.dockerfile.has_healthcheck else "missing" }}
- Runtime user: {{ d.dockerfile.user or "not set" }}
{% endif %}
""",
        diagnosis,
    )


def _render_security(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """# {{ d.name }} Security

## Detected Security Files

{% for file in d.security_files -%}
- `{{ file.path }}`: {{ file.reason }}
{% else -%}
- No security policy or dependency scanning configuration detected.
{% endfor %}

## Baseline Controls

- Keep secrets out of source control.
- Use dependency scanning and lockfile review.
- Run CI on every pull request.
- Use least-privilege credentials for deployment.
- Document vulnerability reporting.

## Recommendations

{% for item in d.recommendations if "security" in item.lower() or "dependency" in item.lower() -%}
- {{ item }}
{% else -%}
- Maintain dependency and container image scanning as the project matures.
{% endfor %}
""",
        diagnosis,
    )


def _render_checklist(diagnosis: ProjectDiagnosis) -> str:
    checks = [
        ("Run tests in CI", diagnosis.github_actions),
        ("Define a repeatable build", diagnosis.docker),
        (
            "Set a non-root Docker runtime user",
            bool(diagnosis.dockerfile and diagnosis.dockerfile.user),
        ),
        (
            "Define a Docker healthcheck or external probe",
            bool(diagnosis.dockerfile and diagnosis.dockerfile.has_healthcheck),
        ),
        ("Document local dependencies", diagnosis.docker_compose),
        ("Expose health checks", diagnosis.health_checks),
        ("Document security reporting", bool(diagnosis.security_files)),
        ("Define deployment manifests", diagnosis.kubernetes),
    ]
    lines = ["# Production Checklist", ""]
    for label, passed in checks:
        marker = "x" if passed else " "
        lines.append(f"- [{marker}] {label}")
    return "\n".join(lines)


def _render_yaml(diagnosis: ProjectDiagnosis) -> str:
    payload = diagnosis.model_dump(mode="json")
    payload["root"] = str(diagnosis.root)
    return yaml.safe_dump(payload, sort_keys=True)


def _render_html(diagnosis: ProjectDiagnosis) -> str:
    recs = "\n".join(f"<li>{html.escape(item)}</li>" for item in diagnosis.recommendations)
    deployments = "\n".join(
        f"<li><code>{html.escape(item.path)}</code>: {html.escape(item.reason)}</li>"
        for item in diagnosis.deployment_files
    )
    language = html.escape(diagnosis.primary_language)
    docker = "yes" if diagnosis.docker else "no"
    kubernetes = "yes" if diagnosis.kubernetes else "no"
    ci = "GitHub Actions" if diagnosis.github_actions else "not detected"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(diagnosis.name)} operations report</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      margin: 2rem;
      max-width: 980px;
      line-height: 1.5;
    }}
    code {{ background: #f2f4f8; padding: .1rem .25rem; border-radius: 4px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: .75rem;
    }}
    .metric {{ border: 1px solid #d7dce5; border-radius: 8px; padding: .75rem; }}
  </style>
</head>
<body>
  <h1>{html.escape(diagnosis.name)} operations report</h1>
  <div class="grid">
    <div class="metric"><strong>Language</strong><br>{language}</div>
    <div class="metric"><strong>Docker</strong><br>{docker}</div>
    <div class="metric"><strong>Kubernetes</strong><br>{kubernetes}</div>
    <div class="metric"><strong>CI</strong><br>{ci}</div>
  </div>
  <h2>Deployment Files</h2>
  <ul>{deployments or "<li>No deployment files detected.</li>"}</ul>
  <h2>Recommendations</h2>
  <ul>{recs or "<li>No immediate recommendations.</li>"}</ul>
</body>
</html>"""


def _deployment_templates(
    diagnosis: ProjectDiagnosis,
    output_dir: Path,
) -> list[GeneratedArtifact]:
    artifacts: list[GeneratedArtifact] = []
    if not diagnosis.docker:
        artifacts.append(
            _write(output_dir / "Dockerfile", _dockerfile(diagnosis), "Dockerfile template")
        )
    if not diagnosis.docker_compose:
        artifacts.append(
            _write(
                output_dir / "docker-compose.yml", _compose(diagnosis), "Docker Compose template"
            )
        )
    if not diagnosis.kubernetes:
        artifacts.append(
            _write(
                output_dir / "kubernetes" / "deployment.yaml",
                _kubernetes(diagnosis),
                "Kubernetes deployment template",
            )
        )
    if not diagnosis.github_actions:
        artifacts.append(
            _write(output_dir / ".github" / "workflows" / "ci.yml", _ci(diagnosis), "CI template")
        )
    if not diagnosis.health_checks:
        artifacts.append(
            _write(output_dir / "health-checks.md", _health_checks(), "health check guidance")
        )
    return artifacts


def _dockerfile(diagnosis: ProjectDiagnosis) -> str:
    if diagnosis.primary_language == "Python":
        return """FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip && python -m pip install .
CMD ["python", "-m", "your_app"]
"""
    if diagnosis.primary_language == "JavaScript/TypeScript":
        return """FROM node:22-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npm", "start"]
"""
    return """FROM debian:stable-slim
WORKDIR /app
COPY . .
CMD ["./start.sh"]
"""


def _compose(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      APP_ENV: development
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
""",
        diagnosis,
    )


def _kubernetes(diagnosis: ProjectDiagnosis) -> str:
    return _template(
        """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ d.name }}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {{ d.name }}
  template:
    metadata:
      labels:
        app: {{ d.name }}
    spec:
      containers:
        - name: app
          image: {{ d.name }}:latest
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
          livenessProbe:
            httpGet:
              path: /live
              port: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: {{ d.name }}
spec:
  selector:
    app: {{ d.name }}
  ports:
    - port: 80
      targetPort: 8080
""",
        diagnosis,
    )


def _ci(diagnosis: ProjectDiagnosis) -> str:
    if diagnosis.primary_language == "Python":
        return """name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e ".[dev]"
      - run: pytest
"""
    return """name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Add project-specific checks here"
"""


def _health_checks() -> str:
    return """# Health Checks

Recommended endpoints:

- `/health`: process is running.
- `/ready`: service can receive traffic.
- `/live`: service should not be restarted.

Include checks for critical dependencies such as databases, queues, object storage,
and external APIs.
"""


def _template(source: str, diagnosis: ProjectDiagnosis) -> str:
    return ENV.from_string(source).render(d=diagnosis)

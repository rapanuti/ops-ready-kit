from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

import yaml

from ops_ready_kit.models import DetectedFile, ProjectDiagnosis

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "node_modules",
}


def scan_repository(root: Path) -> ProjectDiagnosis:
    root = root.resolve()
    files = list(_iter_files(root))
    relative_paths = {_relative(file, root) for file in files}

    diagnosis = ProjectDiagnosis(
        root=root,
        name=root.name,
        languages=_detect_languages(relative_paths),
        frameworks=_detect_frameworks(root, relative_paths),
        package_managers=_detect_package_managers(relative_paths),
        docker="Dockerfile" in relative_paths,
        docker_compose=any(
            path in relative_paths for path in {"docker-compose.yml", "compose.yml"}
        ),
        kubernetes=_has_any_prefix(relative_paths, ("k8s/", "kubernetes/"))
        or any(path.endswith((".k8s.yaml", ".k8s.yml")) for path in relative_paths),
        github_actions=_has_any_prefix(relative_paths, (".github/workflows/",)),
        health_checks=_detect_health_checks(files),
        security_files=_collect_security_files(relative_paths),
        deployment_files=_collect_deployment_files(relative_paths),
        notable_files=_collect_notable_files(relative_paths),
    )

    diagnosis.recommendations = _recommend(diagnosis)
    diagnosis.warnings = _warn(diagnosis)
    return diagnosis


def _iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _detect_languages(paths: set[str]) -> list[str]:
    checks = [
        ("Python", (".py",), {"pyproject.toml", "requirements.txt", "setup.py"}),
        ("JavaScript/TypeScript", (".js", ".jsx", ".ts", ".tsx"), {"package.json"}),
        ("Go", (".go",), {"go.mod"}),
        ("Rust", (".rs",), {"Cargo.toml"}),
        ("Ruby", (".rb",), {"Gemfile"}),
        ("Java", (".java",), {"pom.xml", "build.gradle", "build.gradle.kts"}),
    ]
    found: list[str] = []
    for language, suffixes, markers in checks:
        if markers.intersection(paths) or any(path.endswith(suffixes) for path in paths):
            found.append(language)
    return found


def _detect_frameworks(root: Path, paths: set[str]) -> list[str]:
    frameworks: list[str] = []
    if "manage.py" in paths:
        frameworks.append("Django")
    if "package.json" in paths:
        package_json = root / "package.json"
        try:
            content = package_json.read_text(encoding="utf-8")
        except OSError:
            content = ""
        for name, framework in {
            '"next"': "Next.js",
            '"react"': "React",
            '"vue"': "Vue",
            '"express"': "Express",
        }.items():
            if name in content:
                frameworks.append(framework)
    if any(path.endswith(".py") for path in paths):
        py_text = _read_small_python_files(root, paths)
        if re.search(r"^\s*(from\s+fastapi\s+import|import\s+fastapi\b)", py_text, re.MULTILINE):
            frameworks.append("FastAPI")
        if re.search(r"^\s*(from\s+flask\s+import|import\s+flask\b)", py_text, re.MULTILINE):
            frameworks.append("Flask")
    return sorted(set(frameworks))


def _read_small_python_files(root: Path, paths: set[str]) -> str:
    chunks: list[str] = []
    for path in sorted(p for p in paths if p.endswith(".py"))[:50]:
        full_path = root / path
        try:
            if full_path.stat().st_size <= 50_000:
                chunks.append(full_path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return "\n".join(chunks)


def _detect_package_managers(paths: set[str]) -> list[str]:
    markers = {
        "pip/pyproject": "pyproject.toml",
        "pip/requirements": "requirements.txt",
        "npm": "package-lock.json",
        "pnpm": "pnpm-lock.yaml",
        "yarn": "yarn.lock",
        "poetry": "poetry.lock",
        "uv": "uv.lock",
        "go modules": "go.mod",
        "cargo": "Cargo.lock",
    }
    return [name for name, marker in markers.items() if marker in paths]


def _detect_health_checks(files: list[Path]) -> bool:
    indicators = ("health", "ready", "readiness", "liveness", "/live", "/ready")
    for file in files:
        if file.suffix.lower() not in {".py", ".js", ".ts", ".tsx", ".go", ".yaml", ".yml"}:
            continue
        try:
            text = file.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        if any(indicator in text for indicator in indicators):
            return True
    return False


def _collect_security_files(paths: set[str]) -> list[DetectedFile]:
    names = {
        "SECURITY.md": "security policy",
        ".github/dependabot.yml": "dependency update policy",
        ".github/codeql.yml": "CodeQL configuration",
    }
    return [
        DetectedFile(path=path, reason=reason) for path, reason in names.items() if path in paths
    ]


def _collect_deployment_files(paths: set[str]) -> list[DetectedFile]:
    matches: list[DetectedFile] = []
    for path in sorted(paths):
        if path == "Dockerfile":
            matches.append(DetectedFile(path=path, reason="container build"))
        elif path in {"docker-compose.yml", "compose.yml"}:
            matches.append(DetectedFile(path=path, reason="local orchestration"))
        elif path.startswith(("k8s/", "kubernetes/")) or path.endswith((".k8s.yaml", ".k8s.yml")):
            matches.append(DetectedFile(path=path, reason="Kubernetes manifest"))
        elif path.startswith(".github/workflows/"):
            matches.append(DetectedFile(path=path, reason="GitHub Actions workflow"))
    return matches


def _collect_notable_files(paths: set[str]) -> list[DetectedFile]:
    reasons = {
        "README.md": "project overview",
        "CHANGELOG.md": "release history",
        "CONTRIBUTING.md": "contribution guide",
        "LICENSE": "license",
        ".env.example": "environment template",
    }
    return [
        DetectedFile(path=path, reason=reason) for path, reason in reasons.items() if path in paths
    ]


def _recommend(diagnosis: ProjectDiagnosis) -> list[str]:
    recommendations: list[str] = []
    if not diagnosis.docker:
        recommendations.append(
            "Add a Dockerfile so deployments can build a repeatable container image."
        )
    if not diagnosis.docker_compose:
        recommendations.append("Add docker-compose.yml for local dependency orchestration.")
    if not diagnosis.kubernetes:
        recommendations.append(
            "Add Kubernetes manifests when the service is ready for cluster deployment."
        )
    if not diagnosis.github_actions:
        recommendations.append("Add GitHub Actions CI for tests, linting, and type checking.")
    if not diagnosis.health_checks:
        recommendations.append("Expose health, readiness, and liveness endpoints.")
    if not diagnosis.security_files:
        recommendations.append("Add SECURITY.md and dependency scanning configuration.")
    return recommendations


def _warn(diagnosis: ProjectDiagnosis) -> list[str]:
    warnings: list[str] = []
    if diagnosis.primary_language == "unknown":
        warnings.append(
            "No primary language detected; generated artifacts use conservative placeholders."
        )
    if diagnosis.docker and not diagnosis.health_checks:
        warnings.append("Containerization detected without obvious health checks.")
    return warnings


def _has_any_prefix(paths: set[str], prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefixes) for path in paths)


def read_yaml(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

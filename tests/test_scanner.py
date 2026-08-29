from pathlib import Path

from ops_ready_kit.scanner import scan_repository


def test_scan_detects_python_project(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    (tmp_path / "app.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8"
    )
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")

    diagnosis = scan_repository(tmp_path)

    assert diagnosis.primary_language == "Python"
    assert "FastAPI" in diagnosis.frameworks
    assert diagnosis.github_actions is True
    assert diagnosis.docker is False


def test_scan_collects_deployment_files(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (tmp_path / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
    (tmp_path / "k8s").mkdir()
    (tmp_path / "k8s" / "deployment.yaml").write_text("apiVersion: apps/v1\n", encoding="utf-8")

    diagnosis = scan_repository(tmp_path)

    assert diagnosis.docker is True
    assert diagnosis.docker_compose is True
    assert diagnosis.kubernetes is True
    assert {file.path for file in diagnosis.deployment_files} == {
        "Dockerfile",
        "docker-compose.yml",
        "k8s/deployment.yaml",
    }

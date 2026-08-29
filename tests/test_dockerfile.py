from pathlib import Path

from ops_ready_kit.dockerfile import parse_dockerfile
from ops_ready_kit.scanner import scan_repository


def test_parse_dockerfile_extracts_operational_signals(tmp_path: Path) -> None:
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(
        """FROM python:3.12-slim AS runtime
WORKDIR /app
COPY . .
RUN python -m pip install .
EXPOSE 8080/tcp
USER app
HEALTHCHECK CMD curl -f http://localhost:8080/health
CMD ["python", "-m", "demo"]
""",
        encoding="utf-8",
    )

    info = parse_dockerfile(dockerfile)

    assert info.base_images == ["python:3.12-slim"]
    assert info.exposed_ports == ["8080/tcp"]
    assert info.has_healthcheck is True
    assert info.user == "app"
    assert info.workdir == "/app"
    assert info.command == 'CMD ["python", "-m", "demo"]'
    assert info.copy_steps == 1
    assert info.run_steps == 1


def test_scan_adds_dockerfile_warnings(tmp_path: Path) -> None:
    (tmp_path / "Dockerfile").write_text(
        "FROM python:3.12-slim\nCMD python app.py\n", encoding="utf-8"
    )

    diagnosis = scan_repository(tmp_path)

    assert diagnosis.dockerfile is not None
    assert diagnosis.dockerfile.base_images == ["python:3.12-slim"]
    assert "Dockerfile does not set USER" in "\n".join(diagnosis.warnings)
    assert "HEALTHCHECK" in "\n".join(diagnosis.recommendations)

from pathlib import Path

from ops_ready_kit.generator import generate_all
from ops_ready_kit.models import ProjectDiagnosis


def test_generate_all_writes_core_artifacts(tmp_path: Path) -> None:
    diagnosis = ProjectDiagnosis(root=tmp_path, name="demo", languages=["Python"])
    output = tmp_path / "out"

    artifacts = generate_all(diagnosis, output)

    assert output.joinpath("RUNBOOK.md").exists()
    assert output.joinpath("ARCHITECTURE.md").exists()
    assert output.joinpath("report.html").exists()
    assert output.joinpath("diagnosis.yaml").exists()
    assert any(artifact.path.name == "Dockerfile" for artifact in artifacts)
    assert "demo Runbook" in output.joinpath("RUNBOOK.md").read_text(encoding="utf-8")

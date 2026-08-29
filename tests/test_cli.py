from pathlib import Path

from typer.testing import CliRunner

from ops_ready_kit.cli import app


def test_cli_analyze_generates_output(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")
    output = tmp_path / "output"

    result = CliRunner().invoke(app, ["analyze", str(project), "--output", str(output)])

    assert result.exit_code == 0
    assert output.joinpath("RUNBOOK.md").exists()
    assert "Generated artifacts" in result.stdout

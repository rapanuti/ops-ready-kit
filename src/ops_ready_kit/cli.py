from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from ops_ready_kit import __version__
from ops_ready_kit.generator import generate_all
from ops_ready_kit.scanner import scan_repository

app = typer.Typer(help="Generate operational documentation from repository signals.")
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"ops-ready-kit {__version__}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, help="Show version and exit."),
    ] = None,
) -> None:
    """Analyze repositories and generate operations-ready artifacts."""


@app.command()
def analyze(
    path: Annotated[Path, typer.Argument(help="Repository path to analyze.")] = Path("."),
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Directory where generated artifacts are written."),
    ] = Path("ops-ready-output"),
    deployment_templates: Annotated[
        bool,
        typer.Option(
            help="Generate missing Docker, Compose, Kubernetes, CI, and health check templates."
        ),
    ] = True,
) -> None:
    """Scan a repository and generate operational documentation."""
    if not path.exists() or not path.is_dir():
        raise typer.BadParameter(f"{path} must be an existing directory")

    diagnosis = scan_repository(path)
    artifacts = generate_all(
        diagnosis,
        output,
        include_deployment_templates=deployment_templates,
    )

    table = Table(title=f"ops-ready-kit analysis: {diagnosis.name}")
    table.add_column("Signal")
    table.add_column("Value")
    table.add_row("Primary language", diagnosis.primary_language)
    table.add_row("Frameworks", ", ".join(diagnosis.frameworks) or "none detected")
    table.add_row("Docker", "yes" if diagnosis.docker else "no")
    table.add_row("Kubernetes", "yes" if diagnosis.kubernetes else "no")
    table.add_row("GitHub Actions", "yes" if diagnosis.github_actions else "no")
    table.add_row("Generated artifacts", str(len(artifacts)))
    console.print(table)
    console.print(f"[green]Wrote artifacts to[/green] {output}")

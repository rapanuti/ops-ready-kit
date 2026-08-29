from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class DetectedFile(BaseModel):
    path: str
    reason: str


class ProjectDiagnosis(BaseModel):
    root: Path
    name: str
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    docker: bool = False
    docker_compose: bool = False
    kubernetes: bool = False
    github_actions: bool = False
    health_checks: bool = False
    security_files: list[DetectedFile] = Field(default_factory=list)
    deployment_files: list[DetectedFile] = Field(default_factory=list)
    notable_files: list[DetectedFile] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def primary_language(self) -> str:
        return self.languages[0] if self.languages else "unknown"


class GeneratedArtifact(BaseModel):
    path: Path
    description: str

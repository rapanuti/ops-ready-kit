from __future__ import annotations

from pathlib import Path

from ops_ready_kit.models import DockerfileInfo


def parse_dockerfile(path: Path) -> DockerfileInfo:
    info = DockerfileInfo(path=path.name)
    if not path.exists():
        return info

    logical_lines = _logical_lines(path.read_text(encoding="utf-8", errors="ignore"))
    for line in logical_lines:
        instruction, _, value = line.partition(" ")
        instruction = instruction.upper()
        value = value.strip()
        if instruction == "FROM":
            image = value.split(" AS ", maxsplit=1)[0].split(" as ", maxsplit=1)[0].strip()
            if image:
                info.base_images.append(image)
        elif instruction == "EXPOSE":
            info.exposed_ports.extend(value.split())
        elif instruction == "HEALTHCHECK":
            info.has_healthcheck = True
        elif instruction == "USER":
            info.user = value
        elif instruction == "WORKDIR":
            info.workdir = value
        elif instruction in {"CMD", "ENTRYPOINT"}:
            info.command = f"{instruction} {value}".strip()
        elif instruction == "RUN":
            info.run_steps += 1
        elif instruction in {"COPY", "ADD"}:
            info.copy_steps += 1
    return info


def _logical_lines(content: str) -> list[str]:
    lines: list[str] = []
    pending = ""
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith("\\"):
            pending += line[:-1].strip() + " "
            continue
        lines.append((pending + line).strip())
        pending = ""
    if pending:
        lines.append(pending.strip())
    return lines

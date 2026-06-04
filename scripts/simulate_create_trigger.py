#!/usr/bin/env python3
"""Simulate the deterministic /create trigger preflight.

The real /create skill returns control to the Codex orchestrator after this
stage. This script gives the repository an automated acceptance path for the
artifact that handoff depends on: Docs/Environment/CREATION_CONTEXT.md.
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ENV_DIR = Path("Docs") / "Environment"
CONTEXT_PATH = ENV_DIR / "CREATION_CONTEXT.md"
PROGRESS_PATH = ENV_DIR / "GENERATION_PROGRESS.md"
WRITE_TEST = ".codex_env_write_test"


@dataclass(frozen=True)
class TriggerResult:
    target: Path
    context_path: Path
    directory_status: str
    existing_files: tuple[str, ...]
    hub_status: str
    hub_root: Path | None
    existing_area_slugs: tuple[str, ...]
    pipeline_stage: str
    next_step: str
    resume_from_pass: str | None

    def to_dict(self) -> dict:
        return {
            "target": self.target.as_posix(),
            "context_path": self.context_path.as_posix(),
            "directory_status": self.directory_status,
            "existing_files": list(self.existing_files),
            "hub_status": self.hub_status,
            "hub_root": self.hub_root.as_posix() if self.hub_root else None,
            "existing_area_slugs": list(self.existing_area_slugs),
            "pipeline_stage": self.pipeline_stage,
            "next_step": self.next_step,
            "resume_from_pass": self.resume_from_pass,
        }


def first_line(command: list[str], fallback: str = "not found") -> str:
    if not shutil.which(command[0]):
        return fallback
    try:
        completed = subprocess.run(command, text=True, capture_output=True, timeout=5, check=False)
    except Exception:
        return fallback
    text = (completed.stdout or completed.stderr).strip().splitlines()
    return text[0].strip() if completed.returncode == 0 and text else fallback


def tool_availability() -> dict[str, str]:
    python_version = first_line(["python", "--version"])
    if python_version == "not found":
        python_version = first_line(["python3", "--version"])
    pip_version = first_line(["pip", "--version"])
    if pip_version == "not found":
        pip_version = first_line(["pip3", "--version"])
    powershell = first_line(["powershell", "-Command", "echo available"])
    return {
        "Python": python_version,
        "pip": pip_version,
        "Pandoc": first_line(["pandoc", "--version"]),
        "PowerShell": "available" if powershell == "available" else "not found",
    }


def codex_platform() -> str:
    system = platform.system().lower()
    if system == "windows":
        return "win32"
    if system == "darwin":
        return "darwin"
    return "linux" if system == "linux" else system


def ensure_target(target: Path) -> str:
    if target.exists():
        return "CLEAN"
    target.mkdir(parents=True, exist_ok=True)
    return "CREATED_NEW"


def test_writable(target: Path) -> None:
    probe = target / WRITE_TEST
    probe.write_text("ok\n", encoding="utf-8")
    probe.unlink()


def existing_codex_files(target: Path) -> tuple[str, ...]:
    found = []
    for relative in [".codex", "AGENTS.md", "AGENTS.override.md"]:
        if (target / relative).exists():
            found.append(relative)
    return tuple(found)


def parse_area_slugs(hub_genesis: Path) -> tuple[str, ...]:
    text = hub_genesis.read_text(encoding="utf-8")
    slugs = []
    for line in text.splitlines():
        match = re.search(r"(?:area|slug)\s*[:=-]\s*`?([a-z0-9][a-z0-9-]*)`?", line, re.IGNORECASE)
        if match:
            slugs.append(match.group(1))
            continue
        bullet = re.match(r"\s*-\s*`?([a-z0-9][a-z0-9-]*)`?(?:\s|$)", line)
        if bullet:
            slugs.append(bullet.group(1))
    return tuple(dict.fromkeys(slugs))


def detect_hub(target: Path) -> tuple[str, Path | None, tuple[str, ...]]:
    current = target
    while True:
        hub_genesis = current / "Docs" / "Environment" / "HUB_GENESIS.md"
        if hub_genesis.exists():
            return "HUB_ADD_AREA", current, parse_area_slugs(hub_genesis)
        if current != target and (current / "AGENTS.md").exists() and (current / ".codex").exists():
            return "NONE", None, ()
        if current.parent == current:
            return "NONE", None, ()
        current = current.parent


def parse_resume(progress_path: Path) -> tuple[str, str | None]:
    if not progress_path.exists():
        return "TRIGGER_COMPLETE", None
    text = progress_path.read_text(encoding="utf-8")
    statuses = re.findall(r"Pass\s+([0-9A-Za-z:-]+).*?(COMPLETE|IN_PROGRESS|PENDING|FAIL)", text, re.IGNORECASE)
    if not statuses:
        return "TRIGGER_COMPLETE", None
    has_complete = any(status.upper() == "COMPLETE" for _, status in statuses)
    has_incomplete = any(status.upper() != "COMPLETE" for _, status in statuses)
    if not (has_complete and has_incomplete):
        return "TRIGGER_COMPLETE", None
    for pass_id, status in statuses:
        if status.upper() != "COMPLETE":
            return "RESUME_GENERATION", pass_id
    return "TRIGGER_COMPLETE", None


def context_markdown(
    target: Path,
    created: str,
    directory_status: str,
    existing_files: tuple[str, ...],
    tools: dict[str, str],
    project_type: str,
    notes: str,
    hub_status: str,
    hub_root: Path | None,
    existing_area_slugs: tuple[str, ...],
    pipeline_stage: str,
    resume_from_pass: str | None,
) -> str:
    if pipeline_stage == "RESUME_GENERATION":
        next_step = "GENERATION_PASS_N"
    elif hub_status == "HUB_ADD_AREA":
        next_step = "HUB_ADD_AREA_INTAKE"
    else:
        next_step = "PROFILE_SELECTION"
    existing = ", ".join(existing_files) if existing_files else "none"
    hub_lines = [f"- Status: {hub_status}"]
    if hub_root:
        hub_lines.append(f"- Hub root: {hub_root}")
    if existing_area_slugs:
        hub_lines.append(f"- Existing area slugs: {', '.join(existing_area_slugs)}")
    pipeline_lines = [f"- Stage: {pipeline_stage}"]
    if resume_from_pass:
        pipeline_lines.append(f"- Resume From Pass: {resume_from_pass}")
    pipeline_lines.append(f"- Next: {next_step}")

    return f"""# Creation Context

Created: {created}

## Target
- Path: {target}
- Platform: {codex_platform()}

## Directory Status
- Status: {directory_status}
- Existing files found: {existing}

## Tool Availability
- Python: {tools['Python']}
- pip: {tools['pip']}
- Pandoc: {tools['Pandoc']}
- PowerShell: {tools['PowerShell']}

## User Context
- Stated project type: {project_type}
- Additional notes: {notes}

## Hub Context
{chr(10).join(hub_lines)}

## Pipeline Status
{chr(10).join(pipeline_lines)}
"""


def simulate_trigger(
    target: Path,
    project_type: str = "not specified",
    notes: str = "none",
    created: str | None = None,
) -> TriggerResult:
    target = target.resolve()
    directory_status = ensure_target(target)
    test_writable(target)
    existing_files = existing_codex_files(target)
    if existing_files and directory_status == "CLEAN":
        directory_status = "HAS_EXISTING_ENV"
    hub_status, hub_root, existing_area_slugs = detect_hub(target)
    pipeline_stage, resume_from_pass = parse_resume(target / PROGRESS_PATH)
    if pipeline_stage == "RESUME_GENERATION":
        next_step = "GENERATION_PASS_N"
    elif hub_status == "HUB_ADD_AREA":
        next_step = "HUB_ADD_AREA_INTAKE"
    else:
        next_step = "PROFILE_SELECTION"
    created_value = created or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    context = context_markdown(
        target=target,
        created=created_value,
        directory_status=directory_status,
        existing_files=existing_files,
        tools=tool_availability(),
        project_type=project_type,
        notes=notes,
        hub_status=hub_status,
        hub_root=hub_root,
        existing_area_slugs=existing_area_slugs,
        pipeline_stage=pipeline_stage,
        resume_from_pass=resume_from_pass,
    )
    context_path = target / CONTEXT_PATH
    context_path.parent.mkdir(parents=True, exist_ok=True)
    context_path.write_text(context, encoding="utf-8")
    return TriggerResult(
        target=target,
        context_path=context_path,
        directory_status=directory_status,
        existing_files=existing_files,
        hub_status=hub_status,
        hub_root=hub_root,
        existing_area_slugs=existing_area_slugs,
        pipeline_stage=pipeline_stage,
        next_step=next_step,
        resume_from_pass=resume_from_pass,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target project directory for /create preflight")
    parser.add_argument("--project-type", default="not specified", help="Stated project type for the context file")
    parser.add_argument("--notes", default="none", help="Additional user notes for the context file")
    parser.add_argument("--created", help="Override Created timestamp for reproducible tests")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary")
    args = parser.parse_args()

    result = simulate_trigger(Path(args.target), args.project_type, args.notes, args.created)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Create trigger context written: {result.context_path}")
        print(f"- directory_status={result.directory_status}")
        print(f"- hub_status={result.hub_status}")
        print(f"- pipeline_stage={result.pipeline_stage}")
        print(f"- next={result.next_step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

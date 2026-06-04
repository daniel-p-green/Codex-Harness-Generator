#!/usr/bin/env python3
"""Plan how to adopt a generated Codex harness into an existing project.

The planner is intentionally non-destructive. It inspects project metadata,
creates or reads a generated harness blueprint, and reports which files would be
added or would conflict if copied into the project.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import tempfile
from pathlib import Path

from generate_minimal_harness import PROFILES, generate
from inspect_project import build_payload as build_inspection_payload


DEFAULT_GENERATED_DATE = "2026-06-04"
DEFAULT_IGNORED_DIRS = {".git", "__pycache__"}


def iter_blueprint_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_dir() or any(part in DEFAULT_IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path.relative_to(root))
    return files


def classify_file(project: Path, blueprint: Path, relative: Path) -> dict:
    target = project / relative
    source = blueprint / relative
    if not target.exists():
        status = "add"
        action = "copy generated file"
    elif target.is_dir():
        status = "conflict"
        action = "target path is a directory; choose a different adoption path"
    elif filecmp.cmp(source, target, shallow=False):
        status = "identical"
        action = "no action"
    else:
        status = "conflict"
        action = "review and merge manually; do not overwrite blindly"
    return {
        "path": relative.as_posix(),
        "status": status,
        "action": action,
    }


def build_summary(items: list[dict]) -> dict[str, int]:
    summary = {"add": 0, "conflict": 0, "identical": 0}
    for item in items:
        summary[item["status"]] = summary.get(item["status"], 0) + 1
    return summary


def write_report(path: Path, payload: dict) -> Path:
    lines = [
        "# Harness Adoption Plan",
        "",
        "Flow: non-destructive plan for adopting a generated Codex harness into an existing project.",
        f"Project label: {payload['project']}",
        f"Selected profile: {payload['profile']}",
        f"Selection source: {payload['selection_source']}",
        f"Files scanned: {payload['inspection']['files_scanned']}{' (truncated)' if payload['inspection']['truncated'] else ''}",
        "",
        "## Summary",
        "",
        f"- Add: {payload['summary'].get('add', 0)}",
        f"- Conflicts: {payload['summary'].get('conflict', 0)}",
        f"- Identical: {payload['summary'].get('identical', 0)}",
        "",
        "## Recommended Steps",
        "",
        "1. Review all conflict rows before copying any generated files.",
        "2. Copy only add rows first.",
        "3. Merge conflict rows by hand, preserving existing project-specific instructions.",
        "4. Run the generated `scripts/check-harness.py` after adoption.",
        "5. Record a task trial after the first real Codex task.",
        "",
        "## File Plan",
        "",
        "| Path | Status | Action |",
        "|---|---|---|",
    ]
    for item in payload["files"]:
        lines.append(f"| `{item['path']}` | {item['status']} | {item['action']} |")
    lines.extend(
        [
            "",
            "## Privacy Boundary",
            "",
            "- This plan records metadata, relative paths, and file existence/content equality.",
            "- It does not include source file contents, absolute local paths, secrets, or raw logs.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def build_payload(
    project: Path,
    profile: str | None,
    project_name: str | None,
    harness: Path | None,
    max_files: int,
    limit: int,
    generated_date: str,
    source_label: str | None,
) -> dict:
    if not project.exists():
        raise SystemExit(f"Project path does not exist: {project}")
    if not project.is_dir():
        raise SystemExit(f"Project path must be a directory: {project}")
    if limit < 1:
        raise SystemExit("--limit must be at least 1")

    inspection = build_inspection_payload(project, max_files=max_files, limit=limit)
    selected_profile = profile or inspection["recommended_profile"]
    if selected_profile not in PROFILES:
        supported = ", ".join(sorted(PROFILES))
        raise SystemExit(f"Unsupported --profile {selected_profile!r}. Supported profiles: {supported}")

    project_label = source_label or project.name
    selection_source = "explicit --profile" if profile else "metadata inspection"

    if harness is not None:
        if not harness.exists() or not harness.is_dir():
            raise SystemExit(f"Harness path must be an existing directory: {harness}")
        files = [classify_file(project, harness, relative) for relative in iter_blueprint_files(harness)]
        blueprint_label = harness.name
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            blueprint = Path(temp_dir) / "generated-harness"
            generate(
                blueprint,
                project_name or inspection["project"],
                selected_profile,
                force=True,
                generated_date=generated_date,
            )
            files = [classify_file(project, blueprint, relative) for relative in iter_blueprint_files(blueprint)]
        blueprint_label = f"generated {selected_profile} blueprint"

    summary = build_summary(files)
    return {
        "status": "pass",
        "project": project_label,
        "profile": selected_profile,
        "selection_source": selection_source,
        "blueprint": blueprint_label,
        "inspection": {
            "files_scanned": inspection["files_scanned"],
            "truncated": inspection["truncated"],
            "inferred_brief": inspection["inferred_brief"],
            "recommended_profile": inspection["recommended_profile"],
            "confidence": inspection["confidence"],
        },
        "summary": summary,
        "files": files,
        "conflicts": [item for item in files if item["status"] == "conflict"],
    }


def format_payload(payload: dict) -> str:
    lines = [
        f"Harness adoption plan: {payload['status'].upper()}",
        f"- project: {payload['project']}",
        f"- selected profile: {payload['profile']}",
        f"- add: {payload['summary'].get('add', 0)}",
        f"- conflicts: {payload['summary'].get('conflict', 0)}",
        f"- identical: {payload['summary'].get('identical', 0)}",
    ]
    if payload["conflicts"]:
        lines.append("")
        lines.append("Conflicts:")
        for item in payload["conflicts"]:
            lines.append(f"- {item['path']}: {item['action']}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Existing project directory to adopt a harness into")
    parser.add_argument("--profile", help="Starter profile override; defaults to inspection recommendation")
    parser.add_argument("--project-name", help="Project name for generated blueprint docs")
    parser.add_argument("--harness", help="Existing generated harness blueprint to compare instead of creating one")
    parser.add_argument("--max-files", type=int, default=800, help="Maximum project files to inspect")
    parser.add_argument("--limit", type=int, default=3, help="Number of inspection recommendations to consider")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for temporary blueprint docs")
    parser.add_argument("--source-label", help="Public-safe label for the inspected project")
    parser.add_argument("--report", help="Write a Markdown adoption plan to this path")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = build_payload(
        project=Path(args.project),
        profile=args.profile,
        project_name=args.project_name,
        harness=Path(args.harness) if args.harness else None,
        max_files=args.max_files,
        limit=args.limit,
        generated_date=args.generated_date,
        source_label=args.source_label,
    )
    if args.report:
        report = write_report(Path(args.report), payload)
        payload["report"] = report.as_posix()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_payload(payload), end="")
        if args.report:
            print(f"- report: {payload['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

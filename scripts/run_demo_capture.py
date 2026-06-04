#!/usr/bin/env python3
"""Create a short, reproducible demo capture for a generated Codex harness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_brief_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE, append_manifest_entry, run_brief_acceptance
from validate_generated_harness import validate_path


DEMO_CAPTURE_PATH = Path("Docs") / "Environment" / "DEMO_CAPTURE.md"


def first_heading(path: Path) -> str:
    if not path.is_file():
        return "missing"
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return "untitled"


def write_demo_capture(
    target: Path,
    brief: str,
    project_name: str,
    display_target: str,
    target_label: str | None,
    payload: dict,
    validation: dict,
) -> Path:
    target_path = Path(payload["target"])
    selected = payload["recommendations"]["recommendations"][0]
    profile_selection = Path(payload["profile_selection"]).relative_to(target_path)
    agents_path = Path("AGENTS.md")
    report_path = target / DEMO_CAPTURE_PATH
    command = (
        f'python scripts/codex_harness.py demo-capture {display_target} --brief "{brief}" '
        f'--project-name "{project_name}"'
    )
    if target_label:
        command += f" --target-label {target_label}"
    command += " --force"
    lines = [
        "# Demo Capture",
        "",
        "Purpose: show the reproducible `codex-harness init --brief` path without private data.",
        "",
        "## Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## Generated Harness",
        "",
        f"- Target: {display_target}",
        f"- Brief: {brief}",
        f"- Selected profile: {payload['profile']}",
        f"- Selection confidence: {selected['confidence']}",
        f"- Selection evidence: `{profile_selection.as_posix()}`",
        f"- Primary instruction surface: `{agents_path.as_posix()}` ({first_heading(target / agents_path)})",
        "",
        "## Verification",
        "",
        f"- Brief acceptance: {payload['status']}",
        f"- Eval score: {validation['eval']['score']}",
        f"- Offline smoke: {validation['smoke']['offline']['status']}",
        f"- Local harness check: {validation['smoke']['local_check']['status']}",
        f"- Combined validation: {validation['status']}",
        "",
        "## Reviewer Walkthrough",
        "",
        "1. Open `Docs/Environment/PROFILE_SELECTION.md` to inspect why the profile was selected.",
        "2. Open `AGENTS.md` to inspect the generated Codex-facing instruction surface.",
        "3. Run `python scripts/check-harness.py` inside this generated harness.",
        "4. From the generator repo, run `python scripts/codex_harness.py validate <this-harness>`.",
        "",
        "## Limits",
        "",
        "- This is a deterministic public-safe demo, not external adoption proof.",
        "- It proves the installed-style brief path can generate and validate an inspectable harness.",
        "- It does not prove every future live model-mediated `/create` run will be ideal.",
    ]
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    append_manifest_entry(target, DEMO_CAPTURE_PATH)
    return report_path


def run_demo_capture(
    target: Path,
    brief: str,
    project_name: str | None,
    notes: str,
    force: bool,
    generated_date: str,
    created: str,
    limit: int,
    allow_low_confidence: bool,
    target_label: str | None = None,
) -> dict:
    payload = run_brief_acceptance(
        target=target,
        brief=brief,
        project_name=project_name,
        notes=notes,
        force=force,
        generated_date=generated_date,
        created=created,
        limit=limit,
        allow_low_confidence=allow_low_confidence,
        target_label=target_label,
    )
    target_path = Path(payload["target"])
    validation = validate_path(target_path, min_score=90)
    resolved_project_name = project_name or target_path.name
    display_target = target_label or target.as_posix()
    report_path = write_demo_capture(target_path, brief, resolved_project_name, display_target, target_label, payload, validation)
    payload.update(
        {
            "demo_capture": report_path.as_posix(),
            "display_target": display_target,
            "project_name": resolved_project_name,
            "validation": validation,
            "status": "pass" if payload["status"] == "pass" and validation["status"] == "pass" else "fail",
        }
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target project directory for the demo harness")
    parser.add_argument("--brief", required=True, help="Short project brief used to select a deterministic profile")
    parser.add_argument("--project-name", help="Human-readable project name")
    parser.add_argument("--notes", default="short reproducible demo capture", help="Notes for creation context")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = run_demo_capture(
        target=Path(args.target),
        brief=args.brief,
        project_name=args.project_name,
        notes=args.notes,
        force=args.force,
        generated_date=args.generated_date,
        created=args.created,
        limit=args.limit,
        allow_low_confidence=args.allow_low_confidence,
        target_label=args.target_label,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Demo capture: {payload['status'].upper()}")
        print(f"- target: {payload['target']}")
        print(f"- selected profile: {payload['profile']}")
        print(f"- validation: {payload['validation']['status'].upper()} score={payload['validation']['eval']['score']}")
        print(f"- report: {payload['demo_capture']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

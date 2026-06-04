#!/usr/bin/env python3
"""Run a deterministic preset /create acceptance flow.

This stitches together the two deterministic pieces that model the product
pipeline: trigger preflight writes CREATION_CONTEXT.md, then preset generation
writes a complete Codex harness into the same target without deleting the
handoff artifact. The final harness is evaluated and smoke-checked.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from eval_generated_harness import evaluate
from generate_minimal_harness import CREATION_CONTEXT_PATH, PROFILES, generate
from simulate_create_trigger import simulate_trigger
from smoke_generated_harness import smoke_offline


ACCEPTANCE_REPORT_PATH = Path("Docs") / "Environment" / "CREATE_ACCEPTANCE_REPORT.md"
DEFAULT_GENERATED_DATE = "2026-06-04"
DEFAULT_CREATED = "2026-06-04T12:00:00Z"


def append_manifest_entry(target: Path, entry: Path) -> None:
    manifest = target / "Docs" / "Environment" / "MANIFEST.md"
    text = manifest.read_text(encoding="utf-8")
    line = f"- {entry.as_posix()}"
    if line not in text.splitlines():
        manifest.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")


def write_acceptance_report(target: Path, profile: str, eval_result: dict, smoke_result: dict) -> None:
    status = "PASS" if eval_result["status"] == "pass" and smoke_result["status"] == "pass" else "FAIL"
    report = f"""# Create Acceptance Report

Status: {status}.

## Scenario

- Flow: deterministic preset `/create` acceptance
- Profile: {profile}
- Trigger artifact: {CREATION_CONTEXT_PATH.as_posix()}
- Generated harness: AGENTS.md, .codex/config.toml, .codex/agents, .agents/skills, rules, and environment docs

## Verification

- Generated harness eval: {eval_result['status'].upper()} score={eval_result['score']} failures={eval_result['failure_count']} warnings={eval_result['warning_count']}
- Offline smoke: {smoke_result['status'].upper()}
"""
    (target / ACCEPTANCE_REPORT_PATH).write_text(report, encoding="utf-8")
    append_manifest_entry(target, ACCEPTANCE_REPORT_PATH)


def run_acceptance(
    target: Path,
    profile: str,
    project_name: str | None,
    project_type: str,
    notes: str,
    force: bool,
    generated_date: str,
    created: str,
) -> dict:
    target = target.resolve()
    if profile not in PROFILES:
        supported = ", ".join(sorted(PROFILES))
        raise SystemExit(f"Unsupported --profile {profile!r}. Supported profiles: {supported}")
    if target.exists() and any(target.iterdir()):
        if not force:
            raise SystemExit(f"Target is not empty. Re-run with --force to replace it: {target}")
        shutil.rmtree(target)

    trigger = simulate_trigger(target, project_type=project_type, notes=notes, created=created)
    generate(
        target,
        project_name=project_name,
        profile_slug=profile,
        force=False,
        generated_date=generated_date,
        allow_creation_context=True,
    )
    if not (target / CREATION_CONTEXT_PATH).is_file():
        raise SystemExit(f"Create trigger context was not preserved: {target / CREATION_CONTEXT_PATH}")

    eval_result = evaluate(target)
    smoke_result = smoke_offline(target)
    write_acceptance_report(target, profile, eval_result, smoke_result)
    final_eval_result = evaluate(target)
    status = "pass" if final_eval_result["status"] == "pass" and smoke_result["status"] == "pass" else "fail"
    return {
        "status": status,
        "target": target.as_posix(),
        "profile": profile,
        "trigger": trigger.to_dict(),
        "eval": final_eval_result,
        "smoke": smoke_result,
        "acceptance_report": (target / ACCEPTANCE_REPORT_PATH).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target project directory for deterministic /create acceptance")
    parser.add_argument("--profile", default="software-development", help="Deterministic starter profile")
    parser.add_argument("--project-name", help="Human-readable project name")
    parser.add_argument("--project-type", default="not specified", help="Stated project type for CREATION_CONTEXT.md")
    parser.add_argument("--notes", default="none", help="Additional notes for CREATION_CONTEXT.md")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = run_acceptance(
        target=Path(args.target),
        profile=args.profile,
        project_name=args.project_name,
        project_type=args.project_type,
        notes=args.notes,
        force=args.force,
        generated_date=args.generated_date,
        created=args.created,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Create acceptance: {payload['status'].upper()}")
        print(f"- target: {payload['target']}")
        print(f"- profile: {payload['profile']}")
        print(f"- eval: {payload['eval']['status'].upper()} score={payload['eval']['score']}")
        print(f"- smoke: {payload['smoke']['status'].upper()}")
        print(f"- report: {payload['acceptance_report']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

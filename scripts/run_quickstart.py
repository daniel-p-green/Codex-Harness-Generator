#!/usr/bin/env python3
"""Run the first-use Codex harness path end to end."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from generate_minimal_harness import PROFILES
from run_brief_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE, run_brief_acceptance
from run_create_acceptance import append_manifest_entry
from validate_generated_harness import validate_path


DEFAULT_BRIEF = "RAG app with prompts, evals, and retrieval checks"
DEFAULT_TARGET = "/tmp/codex-quickstart-harness"
QUICKSTART_REPORT = Path("Docs") / "Environment" / "QUICKSTART_REPORT.md"


def build_preflight_payload(min_python: tuple[int, int] = (3, 10), min_profiles: int = 20) -> dict:
    checks = []
    current = sys.version_info
    checks.append(
        {
            "name": "python_version",
            "status": "pass" if (current.major, current.minor) >= min_python else "fail",
            "detail": f"{current.major}.{current.minor}.{current.micro}; required >= {min_python[0]}.{min_python[1]}",
        }
    )
    profile_count = len(PROFILES)
    checks.append(
        {
            "name": "profile_catalog",
            "status": "pass" if profile_count >= min_profiles else "fail",
            "detail": f"{profile_count} supported profiles; required >= {min_profiles}",
        }
    )
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "readiness": "quickstart prerequisites are available",
        "checks": checks,
    }


def run_local_eval(target: Path, min_successes: int = 0) -> dict:
    script = target / "scripts" / "run-harness-evals.py"
    if not script.is_file():
        return {
            "status": "fail",
            "command": [sys.executable, script.as_posix(), "--json"],
            "returncode": 1,
            "stdout": "",
            "stderr": "scripts/run-harness-evals.py is missing.",
        }
    command = [sys.executable, script.as_posix(), "--min-successes", str(min_successes), "--json"]
    completed = subprocess.run(command, cwd=target, text=True, capture_output=True, check=False)
    payload = {
        "status": "pass" if completed.returncode == 0 else "fail",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.stdout.strip().startswith("{"):
        try:
            payload["payload"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload["parse_error"] = "local eval stdout was not valid JSON"
    return payload


def write_report(target: Path, payload: dict) -> Path:
    path = target / QUICKSTART_REPORT
    lines = [
        "# Quickstart Report",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Target: {payload['target']}",
        f"Brief: {payload['brief']}",
        f"Selected profile: {payload['profile']}",
        "",
        "## Checks",
        "",
        f"- Preflight: {payload['doctor']['status'].upper()}",
        f"- Init: {payload['init']['status'].upper()}",
        f"- Validate: {payload['validate']['status'].upper()}",
        f"- Local eval: {payload['local_eval']['status'].upper()}",
        "",
        "## Key Files",
        "",
        "- `Docs/GETTING_STARTED.md`",
        "- `Docs/Environment/PROFILE_SELECTION.md`",
        "- `Docs/Environment/EVAL_REPORT.md`",
        "- `Docs/Environment/TASK_TRIALS.md`",
        "- `Docs/Environment/IMPROVEMENT_LOG.md`",
        "- `Docs/Environment/QUICKSTART_REPORT.md`",
        "",
        "## Next Useful Commands",
        "",
        "```bash",
        "python scripts/check-harness.py",
        "python scripts/run-harness-evals.py --json",
        'python scripts/record-task-trial.py --task "first useful task" --outcome success --evidence "public-safe artifact" --verification "command or reviewer check" --privacy-review "public-safe summary only" --limitations "one quickstart task"',
        "```",
        "",
        "From the generator repo:",
        "",
        "```bash",
        f"codex-harness validate {payload['target']}",
        f"codex-harness evidence-packet {payload['target']} --harness-label \"quickstart harness\"",
        "```",
        "",
        "## Claim Boundary",
        "",
        "This quickstart proves that the generated harness can be created, validated,",
        "and locally evaluated. It does not prove external adoption, production",
        "readiness, compliance, or long-term task quality.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    append_manifest_entry(target, QUICKSTART_REPORT)
    return path


def build_payload(args: argparse.Namespace) -> dict:
    target = Path(args.target).expanduser().resolve()
    doctor = build_preflight_payload()
    init_payload = run_brief_acceptance(
        target=target,
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
    validate = validate_path(target, min_score=args.min_score)
    local_eval = run_local_eval(target, min_successes=args.min_successes)
    status = "pass" if all(
        item["status"] == "pass"
        for item in (doctor, init_payload, validate, local_eval)
    ) else "fail"
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "target": target.as_posix(),
        "brief": args.brief,
        "profile": init_payload.get("profile"),
        "doctor": doctor,
        "init": init_payload,
        "validate": validate,
        "local_eval": local_eval,
    }
    if not args.no_write:
        payload["report"] = write_report(target, payload).as_posix()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=DEFAULT_TARGET, help="Generated harness target directory")
    parser.add_argument("--brief", default=DEFAULT_BRIEF, help="Short project brief")
    parser.add_argument("--project-name", default="Quickstart Harness", help="Human-readable project name")
    parser.add_argument("--notes", default="quickstart path", help="Notes for creation context")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--target-label", help="Override target path written inside CREATION_CONTEXT.md")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum validation score")
    parser.add_argument("--min-successes", type=int, default=0, help="Minimum success task trials expected by local eval")
    parser.add_argument("--no-write", action="store_true", help="Do not write QUICKSTART_REPORT.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = build_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Quickstart: {payload['status'].upper()}")
        print(f"- target: {payload['target']}")
        print(f"- selected profile: {payload['profile']}")
        print(f"- validate: {payload['validate']['status'].upper()}")
        print(f"- local eval: {payload['local_eval']['status'].upper()}")
        if "report" in payload:
            print(f"- report: {payload['report']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

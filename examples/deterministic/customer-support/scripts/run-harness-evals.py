#!/usr/bin/env python3
"""Run copied-harness-local eval checks and write an eval report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "Docs/Environment/EVAL_REPORT.md"


def run_command(command: list[str], display_command: list[str]) -> dict:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(display_command),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "status": "pass" if completed.returncode == 0 else "fail",
    }


def parse_json_stdout(result: dict) -> dict:
    if not result["stdout"]:
        return {}
    try:
        return json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {}


def build_payload(min_successes: int) -> dict:
    checks = {
        "local_check": run_command(
            [sys.executable, "scripts/check-harness.py"],
            ["python", "scripts/check-harness.py"],
        ),
        "task_trials": run_command(
            [
                sys.executable,
                "scripts/summarize-task-trials.py",
                "--min-successes",
                str(min_successes),
                "--json",
            ],
            [
                "python",
                "scripts/summarize-task-trials.py",
                "--min-successes",
                str(min_successes),
                "--json",
            ],
        ),
        "improvements": run_command(
            [sys.executable, "scripts/summarize-improvements.py", "--json"],
            ["python", "scripts/summarize-improvements.py", "--json"],
        ),
    }
    task_trial_payload = parse_json_stdout(checks["task_trials"])
    improvement_payload = parse_json_stdout(checks["improvements"])
    issues: list[str] = []
    for name, result in checks.items():
        if result["status"] != "pass":
            issues.append(f"{name} failed")
    for issue in task_trial_payload.get("issues", []):
        if issue not in issues:
            issues.append(issue)
    for issue in improvement_payload.get("issues", []):
        if issue not in issues:
            issues.append(issue)
    return {
        "status": "pass" if not issues else "fail",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "min_successes": min_successes,
        "checks": checks,
        "task_trials": task_trial_payload,
        "improvements": improvement_payload,
        "issues": issues,
    }


def write_report(payload: dict) -> Path:
    lines = [
        "# Eval Report",
        "",
        f"Generated: {payload['generated_at']}",
        f"Status: {payload['status'].upper()}",
        f"Minimum success trials required: {payload['min_successes']}",
        "",
        "## Checks",
        "",
    ]
    for name, result in payload["checks"].items():
        lines.append(f"- {name}: {result['status'].upper()} (`{result['command']}`)")
    task_trials = payload.get("task_trials") or {}
    if task_trials:
        lines.extend(
            [
                "",
                "## Task Trials",
                "",
                f"- total: {task_trials.get('total', 0)}",
                f"- complete records: {task_trials.get('complete_records', 0)}",
            ]
        )
        outcomes = task_trials.get("outcomes", {})
        for outcome, count in outcomes.items():
            lines.append(f"- {outcome}: {count}")
    improvements = payload.get("improvements") or {}
    if improvements:
        lines.extend(
            [
                "",
                "## Improvements",
                "",
                f"- total: {improvements.get('total', 0)}",
                f"- complete records: {improvements.get('complete_records', 0)}",
                f"- actionable: {improvements.get('actionable', 0)}",
                f"- applied: {improvements.get('applied', 0)}",
            ]
        )
        for status, count in improvements.get("statuses", {}).items():
            lines.append(f"- {status}: {count}")
    if payload["issues"]:
        lines.extend(["", "## Issues", ""])
        for issue in payload["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.extend(["", "## Issues", "", "- none"])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return REPORT_PATH


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-successes", type=int, default=0, help="Fail unless at least this many success task trials are recorded")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--no-write", action="store_true", help="Do not update Docs/Environment/EVAL_REPORT.md")
    args = parser.parse_args()

    payload = build_payload(min_successes=args.min_successes)
    if not args.no_write:
        write_report(payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Harness evals: {payload['status'].upper()}")
        print(f"- report: {REPORT_PATH.relative_to(ROOT).as_posix()}")
        for name, result in payload["checks"].items():
            print(f"- {name}: {result['status'].upper()}")
        for issue in payload["issues"]:
            print(f"- issue: {issue}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

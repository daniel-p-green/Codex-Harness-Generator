#!/usr/bin/env python3
"""Export a public-safe evidence packet from a generated harness."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from record_usage_case import find_sensitive_text
from usage_from_harness import VALID_OUTCOMES, parse_eval_report, parse_task_entries, summarize_outcomes


DEFAULT_PACKET_NAME = "HARNESS_EVIDENCE_PACKET.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_local_eval(harness: Path, min_successes: int) -> dict:
    script = harness / "scripts" / "run-harness-evals.py"
    if not script.is_file():
        return {
            "status": "fail",
            "returncode": 1,
            "stdout": "",
            "stderr": f"Missing local eval script: {script}",
            "payload": {},
        }
    completed = subprocess.run(
        [
            sys.executable,
            script.as_posix(),
            "--min-successes",
            str(min_successes),
            "--json",
            "--no-write",
        ],
        cwd=harness,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = {}
    if completed.stdout.strip():
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = {}
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "payload": payload,
    }


def complete_task_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        entry
        for entry in entries
        if entry.get("task")
        and entry.get("outcome") in VALID_OUTCOMES
        and entry.get("evidence")
        and entry.get("verification")
        and entry.get("privacy_review")
        and entry.get("limitations")
        and entry.get("limitations", "").lower() not in {"none", "none stated", "not stated"}
    ]


def scan_public_text(payload: dict) -> list[str]:
    return find_sensitive_text(json.dumps(payload, sort_keys=True))


def build_payload(harness: Path, min_successes: int, harness_label: str | None) -> dict:
    if not harness.exists() or not harness.is_dir():
        raise SystemExit(f"Harness path must be an existing directory: {harness}")
    task_trials_path = harness / "Docs" / "Environment" / "TASK_TRIALS.md"
    eval_report_path = harness / "Docs" / "Environment" / "EVAL_REPORT.md"
    if not task_trials_path.is_file():
        raise SystemExit(f"Missing task trials file: {task_trials_path}")
    if not eval_report_path.is_file():
        raise SystemExit(f"Missing eval report file: {eval_report_path}")

    task_entries = parse_task_entries(read_text(task_trials_path))
    complete_entries = complete_task_entries(task_entries)
    eval_report = parse_eval_report(read_text(eval_report_path))
    local_eval = run_local_eval(harness, min_successes=min_successes)
    eval_payload = local_eval.get("payload") or {}
    issues = list(eval_payload.get("issues", []))
    if local_eval["status"] != "pass":
        issues.append("local eval failed")
    public_payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness": harness_label or harness.name,
        "status": "pass" if not issues else "needs-review",
        "min_successes": min_successes,
        "eval_report_status": eval_report.get("status", "unknown"),
        "local_eval_status": local_eval["status"],
        "task_trials": {
            "total": len(task_entries),
            "complete": len(complete_entries),
            "outcomes": summarize_outcomes(task_entries),
        },
        "improvements": {
            "total": (eval_payload.get("improvements") or {}).get("total", 0),
            "actionable": (eval_payload.get("improvements") or {}).get("actionable", 0),
            "applied": (eval_payload.get("improvements") or {}).get("applied", 0),
        },
        "recent_task_trials": complete_entries[:5],
        "issues": sorted(set(issues)),
        "privacy_boundary": [
            "Public-safe summary only.",
            "Do not include raw logs, source code, secrets, personal data, private repository names, email addresses, or local machine paths.",
            "Retain raw evidence privately when the evidence type is private-summary.",
        ],
    }
    findings = scan_public_text(public_payload)
    if findings:
        raise SystemExit("Refusing to export evidence packet with sensitive text: " + ", ".join(findings))
    return public_payload


def write_packet(path: Path, payload: dict) -> Path:
    lines = [
        "# Generated Harness Evidence Packet",
        "",
        f"Generated: {payload['generated_at']}",
        f"Harness label: {payload['harness']}",
        f"Status: {payload['status'].upper()}",
        f"Minimum success trials required: {payload['min_successes']}",
        "",
        "## Privacy Boundary",
        "",
    ]
    for item in payload["privacy_boundary"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Local Eval Summary",
            "",
            f"- Eval report status: {payload['eval_report_status'].upper()}",
            f"- Local eval status: {payload['local_eval_status'].upper()}",
            "",
            "## Task Trials",
            "",
            f"- Total: {payload['task_trials']['total']}",
            f"- Complete records: {payload['task_trials']['complete']}",
        ]
    )
    for outcome, count in payload["task_trials"]["outcomes"].items():
        lines.append(f"- {outcome}: {count}")
    lines.extend(
        [
            "",
            "## Recent Complete Trials",
            "",
        ]
    )
    if payload["recent_task_trials"]:
        for entry in payload["recent_task_trials"]:
            lines.extend(
                [
                    f"### {entry.get('task', 'task')}",
                    "",
                    f"- Outcome: {entry.get('outcome', 'unknown')}",
                    f"- Evidence: {entry.get('evidence', '')}",
                    f"- Verification: {entry.get('verification', '')}",
                    f"- Privacy review: {entry.get('privacy_review', '')}",
                    f"- Limitations: {entry.get('limitations', '')}",
                    "",
                ]
            )
    else:
        lines.append("- No complete task-trial records found.")
    lines.extend(
        [
            "## Improvements",
            "",
            f"- Total: {payload['improvements']['total']}",
            f"- Actionable: {payload['improvements']['actionable']}",
            f"- Applied: {payload['improvements']['applied']}",
            "",
            "## Issues",
            "",
        ]
    )
    if payload["issues"]:
        for issue in payload["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Use this packet to review whether a usage record is justified. If the evidence is public-safe,",
            "convert it with `codex-harness usage-from-harness <harness>` or ask an external reporter to",
            "submit the GitHub External usage report form.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", help="Generated harness directory")
    parser.add_argument("--out", help=f"Packet path; defaults to Docs/Environment/{DEFAULT_PACKET_NAME} inside the harness")
    parser.add_argument("--harness-label", help="Public-safe harness label; defaults to directory name")
    parser.add_argument("--min-successes", type=int, default=0, help="Minimum passing success task trials expected")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    harness = Path(args.harness).resolve()
    payload = build_payload(harness, min_successes=args.min_successes, harness_label=args.harness_label)
    out = Path(args.out) if args.out else harness / "Docs" / "Environment" / DEFAULT_PACKET_NAME
    path = write_packet(out, payload)
    payload["packet"] = path.as_posix()
    if args.json:
        print(json.dumps({"status": "pass", **payload}, indent=2))
    else:
        print(f"Evidence packet: {payload['status'].upper()}")
        print(f"- packet: {path.as_posix()}")
        for issue in payload["issues"]:
            print(f"- issue: {issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

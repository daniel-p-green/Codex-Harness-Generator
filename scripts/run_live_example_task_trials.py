#!/usr/bin/env python3
"""Run live Codex task trials against checked-in generated harness examples.

Eval and smoke checks prove structure. These trials prove something more useful:
Codex can load a generated harness, follow its local instructions, perform a
small realistic task in a temporary copy, and leave a concrete artifact behind.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_EXAMPLE_ROOT = REPO_ROOT / "examples" / "live-create"
DEFAULT_REPORT = LIVE_EXAMPLE_ROOT / "TASK_TRIALS.md"


@dataclass(frozen=True)
class TaskTrial:
    name: str
    example: str
    prompt: str
    seed_files: tuple[tuple[str, str], ...]
    expected_file: str
    expected_terms: tuple[str, ...]


TRIALS = (
    TaskTrial(
        name="markdown-notes-summary",
        example="synthetic-markdown-notes",
        seed_files=(
            (
                "Inbox/planning-sync.md",
                """# Planning Sync

Date: 2026-06-04

- Decision: Keep the launch checklist in one shared Markdown file.
- Action: Mira will draft the checklist by Friday.
- Action: Sol will review public-safe wording before sharing.
- Open question: Should weekly notes include a risks section?
""",
            ),
        ),
        expected_file="Outbox/planning-sync-summary.md",
        expected_terms=("Mira", "Sol", "risks section"),
        prompt="""Read `Inbox/planning-sync.md` and use this generated harness to write
`Outbox/planning-sync-summary.md`. Include a short summary, decisions, action
items, and open questions. Preserve the fake names exactly and keep it
public-safe. Verify the file exists before replying.""",
    ),
    TaskTrial(
        name="python-cli-todo-audit",
        example="synthetic-python-cli",
        seed_files=(
            (
                "notes/cleanup.md",
                """# Cleanup Notes

- TODO(2026-05-01): Remove obsolete parser branch.
- TODO(2026-06-02): Add focused regression fixture.
- Note: keep all data synthetic for demos.
""",
            ),
            (
                "notes/release.md",
                """# Release Notes

- TODO(2026-04-15): Rewrite setup instructions.
- Done: add privacy-safe example data.
""",
            ),
        ),
        expected_file="reports/todo-audit.md",
        expected_terms=("obsolete parser branch", "regression fixture", "setup instructions"),
        prompt="""Inspect the Markdown files under `notes/` and use this generated
harness to write `reports/todo-audit.md`. List each TODO, include its date, and
separate stale items from recent items. Keep all content public-safe. Verify the
report file exists before replying.""",
    ),
    TaskTrial(
        name="data-review-weekly-summary",
        example="synthetic-data-review",
        seed_files=(
            (
                "data/raw/weekly_metrics.csv",
                """week,metric,value,segment
2026-05-18,signups,120,self_serve
2026-05-25,signups,138,self_serve
2026-05-18,activation_rate,0.42,self_serve
2026-05-25,activation_rate,0.47,self_serve
2026-05-18,tickets,31,support
2026-05-25,tickets,26,support
""",
            ),
        ),
        expected_file="reports/weekly/2026-05-25-summary.md",
        expected_terms=("signups", "activation_rate", "tickets"),
        prompt="""Inspect `data/raw/weekly_metrics.csv` and use this generated
harness to write `reports/weekly/2026-05-25-summary.md`. Include row count,
columns, week-over-week changes, and chart-ready notes. Do not invent metric
definitions. Verify the report file exists before replying.""",
    ),
    TaskTrial(
        name="security-review-synthetic-code",
        example="synthetic-security-audit",
        seed_files=(
            (
                "src/demo_app.py",
                '''"""Synthetic vulnerable demo app for public-safe review."""

import os
import sqlite3

DEMO_API_KEY = "fake-demo-key-not-real"


def find_user(name):
    connection = sqlite3.connect("demo.db")
    query = f"select id, email from users where name = '{name}'"
    return connection.execute(query).fetchall()


def read_report(report_name):
    base = "reports/public"
    path = os.path.join(base, report_name)
    with open(path, encoding="utf-8") as handle:
        return handle.read()
''',
            ),
        ),
        expected_file="reports/security-review.md",
        expected_terms=("SQL injection", "hardcoded", "path traversal"),
        prompt="""Inspect `src/demo_app.py` and use this generated security
audit harness to write `reports/security-review.md`. Include exactly these
finding titles when supported by the file: `SQL injection`, `hardcoded API key`,
and `path traversal`. For each finding include severity, affected path,
evidence, why it matters, safe remediation, and verification skipped because no
active testing is authorized. Do not run exploit code or scanners. Verify the
report file exists before replying.""",
    ),
    TaskTrial(
        name="legal-research-synthetic-policy",
        example="synthetic-legal-research",
        seed_files=(
            (
                "sources/synthetic-policy-excerpt.md",
                """# Synthetic Remote Work Policy Excerpt

Jurisdiction: Example State

## Section 2. Notice

An employer must give workers a written remote-work equipment policy before
requiring use of personal devices.

## Section 4. Reimbursement

If the policy requires personal-device use, the employer must reimburse
reasonable documented business expenses within 30 days of receiving a complete
expense record.

## Section 8. Exceptions

This excerpt does not address independent contractors, union agreements, or
tax treatment.
""",
            ),
        ),
        expected_file="reports/legal-research-note.md",
        expected_terms=("not legal advice", "Example State", "Section 4"),
        prompt="""Inspect `sources/synthetic-policy-excerpt.md` and use this
generated legal research harness to write `reports/legal-research-note.md`.
Include jurisdiction, source scope, short answer, source-backed analysis with
citations to section labels, open questions, and a clear `not legal advice`
boundary. Do not invent statutes, cases, deadlines, parties, or legal standards.
Verify the report file exists before replying.""",
    ),
)


def selected_trials(names: list[str] | None) -> list[TaskTrial]:
    if not names:
        return list(TRIALS)
    by_name = {trial.name: trial for trial in TRIALS}
    missing = [name for name in names if name not in by_name]
    if missing:
        raise SystemExit(f"Unknown trial(s): {', '.join(missing)}")
    return [by_name[name] for name in names]


def copy_example(example: str, work_root: Path) -> Path:
    source = LIVE_EXAMPLE_ROOT / example
    if not source.is_dir():
        raise SystemExit(f"Missing live-create example: {source}")
    target = work_root / example
    shutil.copytree(source, target)
    return target


def seed_trial(root: Path, trial: TaskTrial) -> None:
    for relative, content in trial.seed_files:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_codex(root: Path, prompt: str, timeout: int, model: str | None) -> dict:
    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("Codex CLI not found on PATH.")
    command = [
        codex,
        "exec",
        "--cd",
        root.as_posix(),
        "--config",
        'approval_policy="never"',
        "--skip-git-repo-check",
        "--ephemeral",
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    return {
        "command": command[:-1] + ["<prompt>"],
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1200:],
        "stderr_tail": completed.stderr[-1200:],
    }


def verify_trial(root: Path, trial: TaskTrial) -> dict:
    output = root / trial.expected_file
    findings: list[str] = []
    if not output.is_file():
        findings.append(f"missing expected file: {trial.expected_file}")
        text = ""
    else:
        text = output.read_text(encoding="utf-8")
    for term in trial.expected_terms:
        if term.lower() not in text.lower():
            findings.append(f"missing expected term in {trial.expected_file}: {term}")
    return {
        "status": "pass" if not findings else "fail",
        "expected_file": trial.expected_file,
        "findings": findings,
    }


def run_trial(trial: TaskTrial, work_root: Path, timeout: int, model: str | None) -> dict:
    root = copy_example(trial.example, work_root)
    seed_trial(root, trial)
    codex_result = run_codex(root, trial.prompt, timeout=timeout, model=model)
    verification = verify_trial(root, trial)
    status = "pass" if codex_result["returncode"] == 0 and verification["status"] == "pass" else "fail"
    return {
        "name": trial.name,
        "example": trial.example,
        "status": status,
        "workspace": root.as_posix(),
        "codex": codex_result,
        "verification": verification,
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Live Example Task Trials",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        "",
        "These trials copy checked-in live-create examples to a temporary",
        "workspace, seed synthetic inputs, run authenticated `codex exec`, and",
        "verify that each generated harness produces the expected output file.",
        "",
        "| Trial | Example | Status | Output |",
        "|---|---|---|---|",
    ]
    for result in payload["results"]:
        verification = result["verification"]
        lines.append(
            f"| `{result['name']}` | `{result['example']}` | {result['status'].upper()} | `{verification['expected_file']}` |"
        )
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- Uses synthetic, public-safe input data only.",
            "- Mutates temporary copies of examples, not the checked-in examples.",
            "- Proves representative task usefulness; it does not prove every",
            "  generated harness will handle every future task perfectly.",
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial", action="append", help="Run one named trial; repeatable")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per Codex task trial in seconds")
    parser.add_argument("--model", help="Optional Codex model override")
    parser.add_argument("--work-root", help="Use an existing work root instead of a temporary directory")
    parser.add_argument("--write-report", default=DEFAULT_REPORT.as_posix(), help="Write Markdown report to this path")
    parser.add_argument("--no-report", action="store_true", help="Do not write a Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    trials = selected_trials(args.trial)
    if args.work_root:
        work_root = Path(args.work_root).resolve()
        if work_root.exists():
            shutil.rmtree(work_root)
        work_root.mkdir(parents=True, exist_ok=True)
        temp_dir = None
    else:
        temp_dir = tempfile.TemporaryDirectory()
        work_root = Path(temp_dir.name)

    try:
        results = [run_trial(trial, work_root, timeout=args.timeout, model=args.model) for trial in trials]
        status = "pass" if all(result["status"] == "pass" for result in results) else "fail"
        payload = {
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": status,
            "results": results,
        }
        if not args.no_report:
            write_report(Path(args.write_report), payload)
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Live example task trials: {status.upper()}")
            for result in results:
                print(f"- {result['name']}: {result['status'].upper()} -> {result['verification']['expected_file']}")
                for finding in result["verification"]["findings"]:
                    print(f"  - {finding}")
        return 0 if status == "pass" else 1
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Append a structured task-trial entry to a generated harness."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_TRIALS_PATH = ROOT / "Docs/Environment/TASK_TRIALS.md"
VALID_OUTCOMES = {"success", "partial", "failed", "inconclusive"}
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(/Users/|/home/|C:\\\\Users\\\\)[^\s]+"),
]


def reject_sensitive(label: str, value: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            raise SystemExit(f"{label} appears to contain sensitive or machine-local data; summarize or redact it first.")


def ensure_entries_section(text: str) -> str:
    if "\n## Entries\n" in text:
        return text.rstrip() + "\n"
    return text.rstrip() + "\n\n## Entries\n\n"


def append_entry(args: argparse.Namespace) -> tuple[Path, dict[str, str]]:
    if args.outcome not in VALID_OUTCOMES:
        raise SystemExit(f"Unsupported outcome: {args.outcome}. Choose one of: {', '.join(sorted(VALID_OUTCOMES))}")
    for label in ["task", "evidence", "verification", "privacy_review", "harness_helped", "limitations"]:
        value = getattr(args, label)
        if value:
            reject_sensitive(label.replace("_", "-"), value)

    text = TASK_TRIALS_PATH.read_text(encoding="utf-8") if TASK_TRIALS_PATH.exists() else "# Task Trials\n"
    text = ensure_entries_section(text)
    entry_date = args.date or date.today().isoformat()
    entry = {
        "date": entry_date,
        "task": args.task,
        "outcome": args.outcome,
        "evidence": args.evidence,
        "verification": args.verification,
        "privacy_review": args.privacy_review,
        "harness_helped": args.harness_helped or "not stated",
        "limitations": args.limitations,
    }
    lines = [
        f"### {entry_date} - {args.outcome.upper()} - {args.task}",
        "",
        f"- Task: {entry['task']}",
        f"- Outcome: {entry['outcome']}",
        f"- Evidence: {entry['evidence']}",
        f"- Verification: {entry['verification']}",
        f"- Privacy review: {entry['privacy_review']}",
        f"- Harness helped: {entry['harness_helped']}",
        f"- Limitations: {entry['limitations']}",
        "",
    ]
    TASK_TRIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASK_TRIALS_PATH.write_text(text + "\n".join(lines), encoding="utf-8")
    return TASK_TRIALS_PATH, entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Short task label")
    parser.add_argument("--outcome", required=True, help="success, partial, failed, or inconclusive")
    parser.add_argument("--evidence", required=True, help="Public-safe artifact, file, or behavior evidence")
    parser.add_argument("--verification", required=True, help="Check, command, review, or inspection that verified the outcome")
    parser.add_argument("--privacy-review", required=True, dest="privacy_review", help="Public-safe privacy review")
    parser.add_argument("--harness-helped", default="", dest="harness_helped", help="How the harness helped, if known")
    parser.add_argument("--limitations", required=True, help="Known limits of this trial")
    parser.add_argument("--date", default="", help="YYYY-MM-DD override for deterministic records")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    path, entry = append_entry(args)
    if args.json:
        print(json.dumps({"status": "pass", "path": path.relative_to(ROOT).as_posix(), "entry": entry}, indent=2))
    else:
        print(f"Recorded task trial in {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Summarize and validate task-trial entries for a generated harness."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_TRIALS_PATH = ROOT / "Docs/Environment/TASK_TRIALS.md"
VALID_OUTCOMES = {"success", "partial", "failed", "inconclusive"}


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            if current is not None:
                entries.append(current)
            title = line.removeprefix("### ").strip()
            parts = title.split(" - ", 2)
            current = {"title": title}
            if len(parts) == 3:
                current.update({"date": parts[0], "outcome": parts[1].lower(), "task": parts[2]})
            continue
        if current is None or not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        current[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    if current is not None:
        entries.append(current)
    return entries


def entry_issues(entry: dict[str, str], index: int) -> list[str]:
    label = entry.get("task") or entry.get("title") or f"entry {index}"
    issues: list[str] = []
    if entry.get("outcome") not in VALID_OUTCOMES:
        issues.append(f"{label}: invalid or missing outcome")
    for field in ["task", "evidence", "verification", "privacy_review", "limitations"]:
        value = entry.get(field, "")
        if not value or value.lower() in {"none", "none stated", "not stated"}:
            issues.append(f"{label}: missing useful {field.replace('_', ' ')}")
    return issues


def build_payload(path: Path, min_successes: int) -> dict:
    if not path.is_file():
        return {
            "status": "fail",
            "path": path.as_posix(),
            "total": 0,
            "outcomes": {},
            "complete_records": 0,
            "issues": [f"Missing task trials file: {path.relative_to(ROOT).as_posix()}"],
        }
    entries = parse_entries(path.read_text(encoding="utf-8"))
    outcomes = Counter(entry.get("outcome", "unknown") for entry in entries)
    issues: list[str] = []
    complete_records = 0
    for index, entry in enumerate(entries, 1):
        current_issues = entry_issues(entry, index)
        if current_issues:
            issues.extend(current_issues)
        else:
            complete_records += 1
    if outcomes.get("success", 0) < min_successes:
        issues.append(f"success count {outcomes.get('success', 0)} is below required minimum {min_successes}")
    return {
        "status": "pass" if not issues else "fail",
        "path": path.relative_to(ROOT).as_posix(),
        "total": len(entries),
        "outcomes": dict(sorted(outcomes.items())),
        "complete_records": complete_records,
        "issues": issues,
    }


def print_text(payload: dict) -> None:
    print(f"Task trials: {payload['status'].upper()}")
    print(f"- total: {payload['total']}")
    print(f"- complete records: {payload['complete_records']}")
    for outcome, count in payload["outcomes"].items():
        print(f"- {outcome}: {count}")
    for issue in payload["issues"]:
        print(f"- issue: {issue}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-successes", type=int, default=0, help="Fail unless at least this many success trials are recorded")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = build_payload(TASK_TRIALS_PATH, min_successes=args.min_successes)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

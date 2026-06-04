#!/usr/bin/env python3
"""Summarize and validate improvement-log entries for a generated harness."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "Docs/Environment/IMPROVEMENT_LOG.md"
VALID_CATEGORIES = {
    "CHECK_GAP",
    "ROUTING_CORRECTION",
    "PERMISSION_FRICTION",
    "SOURCE_FIDELITY",
    "DOMAIN_RISK",
}
VALID_STATUSES = {"open", "proposed", "applied", "rejected"}
EMPTY_VALUES = {"", "none", "none yet", "not run yet", "not stated"}


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
                current.update({"date": parts[0], "category": parts[1], "task": parts[2]})
            continue
        if current is None or not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        current[key.strip().lower().replace(" ", "_").replace("-", "_").replace(",", "")] = value.strip()
    if current is not None:
        entries.append(current)
    return entries


def is_empty(value: str | None) -> bool:
    return (value or "").strip().lower() in EMPTY_VALUES


def entry_issues(entry: dict[str, str], index: int) -> list[str]:
    label = entry.get("task") or entry.get("title") or f"entry {index}"
    issues: list[str] = []
    category = entry.get("category", "")
    status = entry.get("status", "")
    if category not in VALID_CATEGORIES:
        issues.append(f"{label}: invalid or missing category")
    if status not in VALID_STATUSES:
        issues.append(f"{label}: invalid or missing status")
    for field in ["task", "observed_friction", "evidence"]:
        if is_empty(entry.get(field)):
            issues.append(f"{label}: missing useful {field.replace('_', ' ')}")
    if status in {"proposed", "applied"} and is_empty(entry.get("candidate_harness_update")):
        issues.append(f"{label}: proposed/applied entries need a candidate harness update")
    if status == "applied" and is_empty(entry.get("verification_after_update")):
        issues.append(f"{label}: applied entries need verification after update")
    return issues


def build_payload(path: Path) -> dict:
    if not path.is_file():
        return {
            "status": "fail",
            "path": path.as_posix(),
            "total": 0,
            "categories": {},
            "statuses": {},
            "actionable": 0,
            "applied": 0,
            "complete_records": 0,
            "issues": [f"Missing improvement log file: {path.relative_to(ROOT).as_posix()}"],
        }
    entries = parse_entries(path.read_text(encoding="utf-8"))
    categories = Counter(entry.get("category", "unknown") for entry in entries)
    statuses = Counter(entry.get("status", "unknown") for entry in entries)
    issues: list[str] = []
    complete_records = 0
    for index, entry in enumerate(entries, 1):
        current_issues = entry_issues(entry, index)
        if current_issues:
            issues.extend(current_issues)
        else:
            complete_records += 1
    actionable = statuses.get("open", 0) + statuses.get("proposed", 0)
    return {
        "status": "pass" if not issues else "fail",
        "path": path.relative_to(ROOT).as_posix(),
        "total": len(entries),
        "categories": dict(sorted(categories.items())),
        "statuses": dict(sorted(statuses.items())),
        "actionable": actionable,
        "applied": statuses.get("applied", 0),
        "complete_records": complete_records,
        "issues": issues,
    }


def print_text(payload: dict) -> None:
    print(f"Improvements: {payload['status'].upper()}")
    print(f"- total: {payload['total']}")
    print(f"- complete records: {payload['complete_records']}")
    print(f"- actionable: {payload['actionable']}")
    print(f"- applied: {payload['applied']}")
    for category, count in payload["categories"].items():
        print(f"- category {category}: {count}")
    for status, count in payload["statuses"].items():
        print(f"- status {status}: {count}")
    for issue in payload["issues"]:
        print(f"- issue: {issue}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = build_payload(LOG_PATH)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

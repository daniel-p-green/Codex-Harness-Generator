#!/usr/bin/env python3
"""Create a sanitized usage record from a generated harness's local evidence."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from record_usage_case import (
    ALLOWED_EVIDENCE_TYPES,
    DEFAULT_RECORD_DIR,
    DEFAULT_REPORT,
    UsageRecord,
    display_path,
    load_records,
    safe_slug,
    write_record,
    write_report,
)


VALID_OUTCOMES = {"success", "partial", "failed", "inconclusive"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_task_entries(text: str) -> list[dict[str, str]]:
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


def parse_eval_report(text: str) -> dict:
    payload: dict = {"status": "unknown", "checks": {}}
    status_match = re.search(r"^Status:\s*([A-Z]+)\s*$", text, re.MULTILINE)
    if status_match:
        payload["status"] = status_match.group(1).lower()
    for match in re.finditer(r"^-\s*([a-zA-Z0-9_ -]+):\s*([A-Z]+)", text, re.MULTILINE):
        payload["checks"][match.group(1).strip().replace(" ", "_")] = match.group(2).lower()
    return payload


def summarize_outcomes(entries: list[dict[str, str]]) -> dict[str, int]:
    return dict(sorted(Counter(entry.get("outcome", "unknown") for entry in entries).items()))


def derive_outcome(eval_status: str, outcomes: dict[str, int]) -> str:
    if eval_status == "fail":
        return "failed"
    if outcomes.get("success", 0):
        return "success"
    if outcomes.get("partial", 0):
        return "partial"
    if outcomes.get("failed", 0):
        return "failed"
    return "inconclusive"


def build_record(args: argparse.Namespace) -> UsageRecord:
    harness = Path(args.harness).resolve()
    task_trials_path = harness / "Docs/Environment/TASK_TRIALS.md"
    eval_report_path = harness / "Docs/Environment/EVAL_REPORT.md"
    if not task_trials_path.is_file():
        raise SystemExit(f"Missing task trials file: {task_trials_path}")
    if not eval_report_path.is_file():
        raise SystemExit(f"Missing eval report file: {eval_report_path}")

    task_entries = parse_task_entries(read_text(task_trials_path))
    complete_entries = [
        entry
        for entry in task_entries
        if entry.get("task")
        and entry.get("outcome") in VALID_OUTCOMES
        and entry.get("evidence")
        and entry.get("verification")
        and entry.get("privacy_review")
        and entry.get("limitations")
        and entry.get("limitations", "").lower() not in {"none", "none stated", "not stated"}
    ]
    if not complete_entries:
        raise SystemExit("No complete task-trial entries found. Record a task trial before creating usage evidence.")

    eval_payload = parse_eval_report(read_text(eval_report_path))
    outcomes = summarize_outcomes(task_entries)
    derived_outcome = derive_outcome(eval_payload["status"], outcomes)
    outcome = args.outcome or derived_outcome
    if outcome not in VALID_OUTCOMES:
        raise SystemExit(f"Unsupported outcome: {outcome}")

    evidence = [
        f"Generated harness local eval report status: {eval_payload['status'].upper()}.",
        "Recorded task-trial outcomes: "
        + ", ".join(f"{key}={value}" for key, value in outcomes.items()),
    ]
    for entry in complete_entries[:3]:
        evidence.append(f"Task trial `{entry['task']}` recorded as {entry['outcome']}: {entry['evidence']}")
    evidence.extend(args.evidence or [])

    verification = [
        "Copied harness local eval checks: "
        + ", ".join(f"{key}={value}" for key, value in sorted(eval_payload["checks"].items())),
        f"Complete task-trial records reviewed: {len(complete_entries)}.",
    ]
    for entry in complete_entries[:3]:
        verification.append(f"Task trial `{entry['task']}` verification: {entry['verification']}")
    verification.extend(args.verification or [])

    limitations = []
    for entry in complete_entries:
        limitation = entry.get("limitations", "").strip()
        if limitation and limitation not in limitations:
            limitations.append(limitation)
    limitations.extend(args.limitation or [])

    task_summary = args.task_summary or complete_entries[0].get("task", "Generated harness task trial.")
    harness_label = args.harness_label or harness.name
    return UsageRecord(
        slug=safe_slug(args.slug),
        title=args.title,
        generated=args.generated,
        domain=args.domain,
        harness_path=harness_label,
        task_summary=task_summary,
        outcome=outcome,
        evidence_type=args.evidence_type,
        evidence=tuple(evidence),
        verification=tuple(verification),
        privacy_review=args.privacy_review,
        limitations=tuple(limitations),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", help="Generated harness directory with Docs/Environment/TASK_TRIALS.md and EVAL_REPORT.md")
    parser.add_argument("--slug", required=True, help="Stable usage-record slug")
    parser.add_argument("--title", required=True, help="Short usage-record title")
    parser.add_argument("--domain", required=True, help="Usage domain")
    parser.add_argument("--harness-label", help="Public-safe harness path label; defaults to directory name")
    parser.add_argument("--task-summary", help="Public-safe task summary; defaults to the first complete task trial")
    parser.add_argument("--outcome", choices=sorted(VALID_OUTCOMES), help="Override derived outcome")
    parser.add_argument("--evidence-type", choices=sorted(ALLOWED_EVIDENCE_TYPES), required=True)
    parser.add_argument("--evidence", action="append", default=[], help="Additional public-safe evidence item; repeatable")
    parser.add_argument("--verification", action="append", default=[], help="Additional verification item; repeatable")
    parser.add_argument("--privacy-review", required=True, help="Public-safe privacy review note")
    parser.add_argument("--limitation", action="append", default=[], help="Additional limitation; repeatable")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    parser.add_argument("--json", action="store_true", help="Emit the record JSON")
    args = parser.parse_args()

    record = build_record(args)
    record_dir = Path(args.record_dir)
    path = write_record(record_dir, record, force=args.force)
    records = load_records(record_dir)
    write_report(Path(args.report), records)
    if args.json:
        print(json.dumps({"status": "pass", "path": display_path(path), "record": record.to_dict()}, indent=2))
    else:
        print(f"Recorded usage evidence from harness: {display_path(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Append a structured entry to a generated harness improvement log."""

from __future__ import annotations

import argparse
import re
from datetime import date
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


def append_entry(args: argparse.Namespace) -> Path:
    if args.category not in VALID_CATEGORIES:
        raise SystemExit(f"Unsupported category: {args.category}. Choose one of: {', '.join(sorted(VALID_CATEGORIES))}")
    if args.status not in VALID_STATUSES:
        raise SystemExit(f"Unsupported status: {args.status}. Choose one of: {', '.join(sorted(VALID_STATUSES))}")
    for label in ["task", "friction", "evidence", "correction", "candidate_update", "verification"]:
        value = getattr(args, label)
        if value:
            reject_sensitive(label.replace("_", "-"), value)

    text = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else "# Improvement Log\n"
    text = ensure_entries_section(text)
    entry_date = args.date or date.today().isoformat()
    lines = [
        f"### {entry_date} - {args.category} - {args.task}",
        "",
        f"- Task: {args.task}",
        f"- Observed friction: {args.friction}",
        f"- Evidence: {args.evidence}",
        f"- User correction, if any: {args.correction or 'none'}",
        f"- Candidate harness update: {args.candidate_update or 'none yet'}",
        f"- Verification after update: {args.verification or 'not run yet'}",
        f"- Status: {args.status}",
        "",
    ]
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(text + "\n".join(lines), encoding="utf-8")
    return LOG_PATH


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="One of CHECK_GAP, ROUTING_CORRECTION, PERMISSION_FRICTION, SOURCE_FIDELITY, DOMAIN_RISK")
    parser.add_argument("--task", required=True, help="Short task label")
    parser.add_argument("--friction", required=True, help="What went wrong or slowed the work")
    parser.add_argument("--evidence", required=True, help="Public-safe evidence such as file paths, commands, or observed behavior")
    parser.add_argument("--correction", default="", help="User correction, if any")
    parser.add_argument("--candidate-update", default="", dest="candidate_update", help="Possible harness update")
    parser.add_argument("--verification", default="", help="Verification run after applying an update")
    parser.add_argument("--status", default="open", help="open, proposed, applied, or rejected")
    parser.add_argument("--date", default="", help="YYYY-MM-DD override for deterministic records")
    args = parser.parse_args()

    path = append_entry(args)
    print(f"Recorded improvement entry in {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

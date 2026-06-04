#!/usr/bin/env python3
"""Create a privacy-checked usage record from a GitHub issue-form body."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pilot_board
from record_usage_case import (
    ALLOWED_EVIDENCE_TYPES,
    ALLOWED_GENERATION_PATHS,
    ALLOWED_OUTCOMES,
    ALLOWED_SOURCE_TYPES,
    DEFAULT_RECORD_DIR,
    DEFAULT_REPORT,
    UsageRecord,
    display_path,
    load_records,
    validate_record,
    safe_slug,
    write_record,
    write_report,
)


LABEL_MAP = {
    "domain or project type": "domain",
    "generated harness profile or label": "harness_label",
    "evidence type": "evidence_type",
    "source type": "source_type",
    "generation path": "generation_path",
    "outcome": "outcome",
    "public-safe task summary": "task_summary",
    "evidence": "evidence",
    "verification performed": "verification",
    "privacy review": "privacy_review",
    "limitations": "limitations",
}

NO_RESPONSE_VALUES = {"", "_no response_", "no response"}
CONVERTIBLE_PILOT_STATUSES = {"prepared", "invited", "completed"}


def normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def clean_value(value: str) -> str:
    value = value.strip()
    return "" if normalize_label(value) in NO_RESPONSE_VALUES else value


def read_issue_body(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def parse_issue_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_key: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            key = LABEL_MAP.get(normalize_label(heading.group(1)))
            current_key = key
            if key and key not in sections:
                sections[key] = []
            continue
        if current_key:
            sections[current_key].append(line)
    return {key: clean_value("\n".join(lines)) for key, lines in sections.items()}


def parse_items(value: str) -> tuple[str, ...]:
    value = clean_value(value)
    if not value:
        return ()
    items = []
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        bullet = re.match(r"^(?:[-*+]|\d+[.)])\s+(.+)$", stripped)
        item = clean_value((bullet.group(1) if bullet else stripped).strip())
        if item:
            items.append(item)
    return tuple(item for item in items if item)


def require_field(sections: dict[str, str], key: str) -> str:
    value = clean_value(sections.get(key, ""))
    if not value:
        raise SystemExit(f"Issue body is missing required field: {key}")
    return value


def build_record(args: argparse.Namespace) -> UsageRecord:
    sections = parse_issue_sections(read_issue_body(args.issue_body))
    evidence_type = require_field(sections, "evidence_type")
    outcome = require_field(sections, "outcome")
    if evidence_type not in ALLOWED_EVIDENCE_TYPES:
        raise SystemExit(f"Unsupported evidence type in issue body: {evidence_type}")
    if outcome not in ALLOWED_OUTCOMES:
        raise SystemExit(f"Unsupported outcome in issue body: {outcome}")
    source_type = clean_value(sections.get("source_type", "")) or args.source_type
    generation_path = clean_value(sections.get("generation_path", "")) or args.generation_path
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise SystemExit(f"Unsupported source type in issue body: {source_type}")
    if generation_path not in ALLOWED_GENERATION_PATHS:
        raise SystemExit(f"Unsupported generation path in issue body: {generation_path}")

    harness_label = args.harness_label or clean_value(sections.get("harness_label", "")) or "external usage report"
    return UsageRecord(
        slug=safe_slug(args.slug),
        title=args.title,
        generated=args.generated,
        domain=require_field(sections, "domain"),
        harness_path=harness_label,
        task_summary=require_field(sections, "task_summary"),
        outcome=outcome,
        evidence_type=evidence_type,
        source_type=source_type,
        generation_path=generation_path,
        evidence=parse_items(require_field(sections, "evidence")),
        verification=parse_items(require_field(sections, "verification")),
        privacy_review=require_field(sections, "privacy_review"),
        limitations=parse_items(require_field(sections, "limitations")),
    )


def validate_pilot_conversion(record: UsageRecord, pilot_record_dir: Path) -> dict:
    path = pilot_board.default_record_path(pilot_record_dir, record.slug)
    pilot_record = pilot_board.read_record(path)
    errors = pilot_board.validate_record(pilot_record, path)
    if pilot_record.get("status") not in CONVERTIBLE_PILOT_STATUSES:
        errors.append(f"{path.name}: pilot status must be prepared, invited, or completed before conversion")
    for field, usage_value in (
        ("domain", record.domain),
        ("source_type", record.source_type),
        ("generation_path", record.generation_path),
    ):
        pilot_value = str(pilot_record.get(field, "")).strip().casefold()
        if pilot_value != usage_value.strip().casefold():
            errors.append(
                f"{path.name}: pilot {field} mismatch before write: pilot={pilot_record.get(field)!r} usage={usage_value!r}"
            )
    if errors:
        raise SystemExit("Pilot conversion validation failed: " + "; ".join(errors))
    return pilot_record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_body", help="Markdown issue body path, or '-' for stdin")
    parser.add_argument("--slug", required=True, help="Stable usage-record slug")
    parser.add_argument("--title", required=True, help="Short usage-record title")
    parser.add_argument("--harness-label", help="Public-safe harness label override")
    parser.add_argument("--source-type", choices=sorted(ALLOWED_SOURCE_TYPES), default="external")
    parser.add_argument("--generation-path", choices=sorted(ALLOWED_GENERATION_PATHS), default="unknown")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument(
        "--pilot-record-dir",
        help="Optional pilot-board record directory; matching pilot slug is prevalidated, then marked converted after the usage record is written",
    )
    parser.add_argument("--pilot-board-report", default=pilot_board.DEFAULT_REPORT.as_posix())
    parser.add_argument("--pilot-notes", default="converted from external usage issue")
    parser.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    parser.add_argument("--no-write", action="store_true", help="Validate and preview the record without writing files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    record = build_record(args)
    validate_record(record)
    if args.pilot_record_dir:
        validate_pilot_conversion(record, Path(args.pilot_record_dir))
    path = None
    pilot_update = None
    if args.no_write:
        pass
    else:
        record_dir = Path(args.record_dir)
        path = write_record(record_dir, record, force=args.force)
        records = load_records(record_dir)
        write_report(Path(args.report), records)
        if args.pilot_record_dir:
            pilot_update = pilot_board.update_record_file(
                Path(args.pilot_record_dir),
                record.slug,
                "converted",
                notes=args.pilot_notes,
                usage_record=record.slug,
                usage_record_dir=record_dir,
            )
            board_payload = pilot_board.build_payload(Path(args.pilot_record_dir), usage_record_dir=record_dir)
            pilot_board.write_report(Path(args.pilot_board_report), board_payload)
            pilot_update["board_report"] = display_path(Path(args.pilot_board_report))
            pilot_update["board_status"] = board_payload["status"]
            pilot_update["board_readiness"] = board_payload["readiness"]
            if board_payload["status"] != "pass":
                raise SystemExit("Pilot board validation failed: " + "; ".join(board_payload["errors"]))
    if args.json:
        payload = {
            "status": "pass",
            "written": not args.no_write,
            "path": display_path(path) if path is not None else None,
            "record": record.to_dict(),
            "pilot_update": pilot_update,
        }
        print(json.dumps(payload, indent=2))
    else:
        if args.no_write:
            print(f"Validated usage evidence from issue without writing: {record.slug}")
        else:
            print(f"Recorded usage evidence from issue: {display_path(path)}")
            if pilot_update:
                print(f"Converted pilot board record: {display_path(Path(pilot_update['path']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

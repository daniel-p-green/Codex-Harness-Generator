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
    NON_SYNTHETIC_EVIDENCE_TYPES,
    UsageRecord,
    display_path,
    find_sensitive_text,
    load_records,
    validate_record,
    safe_slug,
    write_record,
    write_report,
)


LABEL_MAP = {
    "pilot slug": "pilot_slug",
    "pilot or usage-record slug": "pilot_slug",
    "pilot or usage record slug": "pilot_slug",
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
PILOT_DEFAULT_FIELDS = {
    "title": "title",
    "source_type": "source_type",
    "generation_path": "generation_path",
}
ISSUE_REQUIRED_FIELDS = (
    "pilot_slug",
    "domain",
    "evidence_type",
    "outcome",
    "task_summary",
    "evidence",
    "verification",
    "privacy_review",
    "limitations",
)


def normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def clean_value(value: str) -> str:
    value = value.strip()
    return "" if normalize_label(value) in NO_RESPONSE_VALUES else value


def read_issue_body(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def issue_body_text(args: argparse.Namespace) -> str:
    if not hasattr(args, "_issue_body_text"):
        args._issue_body_text = read_issue_body(args.issue_body)
    return args._issue_body_text


def parse_issue_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_key: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            key = LABEL_MAP.get(normalize_label(heading.group(1)))
            current_key = key
            if key:
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
    current: list[str] = []
    saw_bullet = False

    def flush_current() -> None:
        if not current:
            return
        item = clean_value(" ".join(part.strip() for part in current if part.strip()))
        if item:
            items.append(item)
        current.clear()

    for line in value.splitlines():
        stripped = line.strip()
        if not stripped:
            if current and not saw_bullet:
                flush_current()
            continue
        bullet = re.match(r"^(?:[-*+]|\d+[.)])\s+(.+)$", stripped)
        if bullet:
            saw_bullet = True
            flush_current()
            current.append(bullet.group(1).strip())
        elif current:
            current.append(stripped)
        else:
            current.append(stripped)
    flush_current()
    return tuple(item for item in items if item)


def require_field(sections: dict[str, str], key: str) -> str:
    value = clean_value(sections.get(key, ""))
    if not value:
        raise SystemExit(f"Issue body is missing required field: {key}")
    return value


def resolve_slug(args: argparse.Namespace, *, required: bool = True) -> bool:
    sections = parse_issue_sections(issue_body_text(args))
    issue_slug = clean_value(sections.get("pilot_slug", ""))
    if args.slug:
        args.slug = safe_slug(args.slug)
        return True
    if issue_slug:
        args.slug = safe_slug(issue_slug)
        return True
    args.slug = ""
    if required:
        raise SystemExit("Missing required metadata: --slug or issue field 'Pilot or usage-record slug'.")
    return False


def apply_pilot_defaults(args: argparse.Namespace) -> dict | None:
    args.pilot_defaults_applied = []
    if not args.pilot_record_dir:
        return None
    if not args.slug:
        return None
    slug = safe_slug(args.slug)
    path = pilot_board.default_record_path(Path(args.pilot_record_dir), slug)
    record = pilot_board.read_record(path)
    errors = pilot_board.validate_record(record, path)
    if errors:
        raise SystemExit("Pilot record is invalid: " + "; ".join(errors))
    for arg_name, pilot_field in PILOT_DEFAULT_FIELDS.items():
        if getattr(args, arg_name, None) is None:
            value = record.get(pilot_field)
            setattr(args, arg_name, value)
            if value:
                args.pilot_defaults_applied.append(arg_name)
    args.pilot_harness_label = record.get("harness_label")
    return record


def apply_standalone_defaults(args: argparse.Namespace) -> None:
    args.standalone_defaults_applied = []
    if args.source_type is None:
        args.source_type = "external"
        args.standalone_defaults_applied.append("source_type")
    if args.generation_path is None:
        args.generation_path = "unknown"
        args.standalone_defaults_applied.append("generation_path")


def require_metadata(args: argparse.Namespace) -> None:
    if not args.title:
        raise SystemExit(
            "Missing required metadata: --title. Provide it directly or use --pilot-record-dir with a matching prepared pilot."
        )


def lint_issue_payload(args: argparse.Namespace) -> dict:
    sections = parse_issue_sections(issue_body_text(args))
    errors = []
    warnings = []
    missing_fields = [field for field in ISSUE_REQUIRED_FIELDS if not clean_value(sections.get(field, ""))]
    if args.slug and "pilot_slug" in missing_fields:
        missing_fields.remove("pilot_slug")

    evidence_type = clean_value(sections.get("evidence_type", ""))
    outcome = clean_value(sections.get("outcome", ""))
    source_type = clean_value(sections.get("source_type", "")) or args.source_type
    generation_path = clean_value(sections.get("generation_path", "")) or args.generation_path
    evidence = parse_items(sections.get("evidence", ""))
    verification = parse_items(sections.get("verification", ""))
    limitations = parse_items(sections.get("limitations", ""))
    for field, items in (("evidence", evidence), ("verification", verification), ("limitations", limitations)):
        if not items and field not in missing_fields:
            missing_fields.append(field)

    if missing_fields:
        errors.append("Missing required issue field(s): " + ", ".join(missing_fields))
    if not args.title:
        errors.append("Missing required metadata: --title or matching --pilot-record-dir")
    if "source_type" in getattr(args, "standalone_defaults_applied", []) and not clean_value(sections.get("source_type", "")):
        errors.append("Missing source type: fill the issue field, pass --source-type, or use a matching --pilot-record-dir")
    if "generation_path" in getattr(args, "standalone_defaults_applied", []) and not clean_value(sections.get("generation_path", "")):
        errors.append(
            "Missing generation path: fill the issue field, pass --generation-path, or use a matching --pilot-record-dir"
        )
    if evidence_type and evidence_type not in ALLOWED_EVIDENCE_TYPES:
        errors.append(f"Unsupported evidence type: {evidence_type}")
    if outcome and outcome not in ALLOWED_OUTCOMES:
        errors.append(f"Unsupported outcome: {outcome}")
    if source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"Unsupported source type: {source_type}")
    if generation_path not in ALLOWED_GENERATION_PATHS:
        errors.append(f"Unsupported generation path: {generation_path}")
    if evidence_type in NON_SYNTHETIC_EVIDENCE_TYPES:
        if len(evidence) < 2:
            errors.append("Non-synthetic usage requires at least two evidence bullets")
        if len(verification) < 2:
            errors.append("Non-synthetic usage requires at least two verification bullets")
        if not limitations:
            errors.append("Non-synthetic usage requires at least one limitation")
    if evidence_type == "synthetic":
        warnings.append("Synthetic usage can validate tooling but does not count as external beta-exit proof")

    sensitive_findings = find_sensitive_text(json.dumps(sections, sort_keys=True))
    if sensitive_findings:
        errors.append("Sensitive text detected: " + ", ".join(sensitive_findings))

    inferred_fields = list(getattr(args, "pilot_defaults_applied", []))
    if clean_value(sections.get("harness_label", "")) == "" and getattr(args, "pilot_harness_label", ""):
        inferred_fields.append("harness_label")

    return {
        "status": "pass" if not errors else "fail",
        "readiness": "conversion-ready" if not errors else "needs-input",
        "slug": safe_slug(args.slug) if args.slug else "",
        "title": args.title or "",
        "missing_fields": missing_fields,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "evidence": len(evidence),
            "verification": len(verification),
            "limitations": len(limitations),
        },
        "values": {
            "pilot_slug": args.slug,
            "domain": clean_value(sections.get("domain", "")),
            "evidence_type": evidence_type,
            "outcome": outcome,
            "source_type": source_type,
            "generation_path": generation_path,
            "harness_label": clean_value(sections.get("harness_label", ""))
            or getattr(args, "pilot_harness_label", "")
            or "external usage report",
        },
        "inferred_fields": inferred_fields,
    }


def build_record(args: argparse.Namespace) -> UsageRecord:
    sections = parse_issue_sections(issue_body_text(args))
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

    harness_label = (
        args.harness_label
        or clean_value(sections.get("harness_label", ""))
        or getattr(args, "pilot_harness_label", "")
        or "external usage report"
    )
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue_body", help="Markdown issue body path, or '-' for stdin")
    parser.add_argument("--slug", help="Stable usage-record slug; inferred from issue body when omitted")
    parser.add_argument("--title", help="Short usage-record title; inferred from matching pilot record when available")
    parser.add_argument("--harness-label", help="Public-safe harness label override; inferred from matching pilot record when available")
    parser.add_argument("--source-type", choices=sorted(ALLOWED_SOURCE_TYPES), help="Fallback source type; inferred from matching pilot record when available")
    parser.add_argument("--generation-path", choices=sorted(ALLOWED_GENERATION_PATHS), help="Fallback generation path; inferred from matching pilot record when available")
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
    parser.add_argument("--lint-only", action="store_true", help="Check issue-body readiness without building or writing a usage record")
    parser.add_argument("--no-write", action="store_true", help="Validate and preview the record without writing files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    resolve_slug(args, required=not args.lint_only)
    apply_pilot_defaults(args)
    apply_standalone_defaults(args)
    if args.lint_only:
        payload = lint_issue_payload(args)
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"Issue evidence lint: {payload['readiness']}")
            for error in payload["errors"]:
                print(f"- error: {error}")
            for warning in payload["warnings"]:
                print(f"- warning: {warning}")
        return 0 if payload["status"] == "pass" else 1
    require_metadata(args)
    record = build_record(args)
    validate_record(record)
    if args.pilot_record_dir:
        pilot_board.validate_pre_conversion(
            Path(args.pilot_record_dir),
            record.slug,
            record.domain,
            record.source_type,
            record.generation_path,
        )
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

#!/usr/bin/env python3
"""Audit pilot handoff folders before sending them to reporters."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import export_pilot_handoff
import export_pilot_outreach
import usage_from_issue
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_HANDOFF_AUDIT.md"
REQUIRED_FILES = (
    "README.md",
    "REPORTER_HANDOFF.md",
    "REPORTER_MESSAGE.txt",
    "MAINTAINER_COMMANDS.md",
    "PILOT_PACK.md",
    "USAGE_ISSUE_DRAFT.md",
    "USAGE_REPORT_DRAFT.md",
    "RETURN_PACKET.md",
)
ACCEPTABLE_DRAFT_ERRORS = (
    "Missing required issue field(s):",
    "Non-synthetic usage requires at least two evidence bullets",
    "Non-synthetic usage requires at least two verification bullets",
    "Non-synthetic usage requires at least one limitation",
)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def build_handoff_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        record_dir=args.record_dir,
        usage_record_dir=args.usage_record_dir,
        usage_report=args.usage_report,
        pilot_board_report=args.pilot_board_report,
        out=args.handoff_dir,
        status=args.status,
        slug=args.slug,
    )


def issue_lint_payload(draft: Path, args: argparse.Namespace) -> dict:
    lint_args = argparse.Namespace(
        issue_body=draft.as_posix(),
        slug=None,
        title=None,
        harness_label=None,
        source_type=None,
        generation_path=None,
        generated=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        record_dir=args.usage_record_dir,
        report=args.usage_report,
        pilot_record_dir=args.record_dir,
        pilot_board_report=args.pilot_board_report,
        pilot_notes="handoff audit",
        force=False,
        lint_only=True,
        no_write=True,
        json=True,
    )
    usage_from_issue.resolve_slug(lint_args, required=False)
    usage_from_issue.apply_pilot_defaults(lint_args)
    usage_from_issue.apply_standalone_defaults(lint_args)
    return usage_from_issue.lint_issue_payload(lint_args)


def only_reporter_input_missing(errors: list[str]) -> bool:
    return all(error.startswith(ACCEPTABLE_DRAFT_ERRORS) for error in errors)


def audit_draft(path: Path, record: dict, args: argparse.Namespace) -> dict:
    errors = []
    warnings = []
    sections = usage_from_issue.parse_issue_sections(path.read_text(encoding="utf-8"))
    expected = {
        "pilot_slug": record["slug"],
        "domain": record["domain"],
        "harness_label": record.get("harness_label") or record["title"],
        "source_type": record["source_type"],
        "generation_path": record["generation_path"],
    }
    for key, value in expected.items():
        actual = usage_from_issue.clean_value(sections.get(key, ""))
        if actual != value:
            errors.append(f"USAGE_REPORT_DRAFT.md {key} mismatch: expected {value!r}, found {actual!r}")
    evidence_type = usage_from_issue.clean_value(sections.get("evidence_type", ""))
    if evidence_type != "private-summary":
        errors.append("USAGE_REPORT_DRAFT.md should default evidence type to private-summary for reporter handoffs.")

    try:
        lint_payload = issue_lint_payload(path, args)
    except SystemExit as exc:
        return {
            "path": display_path(path),
            "status": "fail",
            "readiness": "lint-error",
            "errors": errors + [f"USAGE_REPORT_DRAFT.md importer lint failed: {exc}"],
            "warnings": warnings,
            "lint": None,
        }

    if lint_payload["slug"] != record["slug"]:
        errors.append(f"Importer inferred slug {lint_payload['slug']!r}, expected {record['slug']!r}.")
    values = lint_payload["values"]
    for key in ("source_type", "generation_path"):
        if values[key] != record[key]:
            errors.append(f"Importer inferred {key} {values[key]!r}, expected {record[key]!r}.")
    if values["evidence_type"] != "private-summary":
        errors.append("Importer did not read private-summary evidence type from the draft.")
    if values["harness_label"] != (record.get("harness_label") or record["title"]):
        errors.append(
            f"Importer inferred harness label {values['harness_label']!r}, "
            f"expected {(record.get('harness_label') or record['title'])!r}."
        )
    if lint_payload["status"] == "fail" and not only_reporter_input_missing(lint_payload["errors"]):
        errors.extend(f"Unexpected draft lint error: {error}" for error in lint_payload["errors"])
    if lint_payload["readiness"] == "needs-input":
        warnings.append("USAGE_REPORT_DRAFT.md is importer-shaped but still needs reporter evidence before conversion.")

    return {
        "path": display_path(path),
        "status": "pass" if not errors else "fail",
        "readiness": lint_payload["readiness"],
        "errors": errors,
        "warnings": warnings,
        "lint": {
            "status": lint_payload["status"],
            "readiness": lint_payload["readiness"],
            "missing_fields": lint_payload["missing_fields"],
            "errors": lint_payload["errors"],
            "counts": lint_payload["counts"],
            "values": lint_payload["values"],
        },
    }


def audit_file(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return [f"Missing required file: {path.name}"]
    findings = find_sensitive_text(path.read_text(encoding="utf-8"))
    if findings:
        return [f"{path.name} contains sensitive text: {', '.join(findings)}"]
    return []


def audit_record(record: dict, args: argparse.Namespace) -> dict:
    directory = Path(args.handoff_dir) / export_pilot_handoff.safe_slug(record["slug"])
    errors = []
    warnings = []
    files = {}
    for name in REQUIRED_FILES:
        path = directory / name
        file_errors = audit_file(path)
        files[name] = {
            "path": display_path(path),
            "status": "pass" if not file_errors else "fail",
            "errors": file_errors,
        }
        errors.extend(file_errors)

    if not directory.exists():
        errors.append(f"Missing handoff directory: {display_path(directory)}")
    else:
        readme = directory / "README.md"
        reporter_handoff = directory / "REPORTER_HANDOFF.md"
        return_packet = directory / "RETURN_PACKET.md"
        maintainer_commands = directory / "MAINTAINER_COMMANDS.md"
        if readme.exists() and "not usage proof" not in readme.read_text(encoding="utf-8"):
            errors.append("README.md must keep the handoff claim boundary explicit.")
        if reporter_handoff.exists():
            reporter_text = reporter_handoff.read_text(encoding="utf-8")
            if "NEXT_TASK.md" not in reporter_text:
                errors.append("REPORTER_HANDOFF.md must point reporters to NEXT_TASK.md.")
            if "USAGE_REPORT_DRAFT.md" not in reporter_text:
                errors.append("REPORTER_HANDOFF.md must point reporters to USAGE_REPORT_DRAFT.md.")
            if "not usage proof" not in reporter_text:
                errors.append("REPORTER_HANDOFF.md must keep the handoff claim boundary explicit.")
            if "RETURN_PACKET.md" not in reporter_text:
                errors.append("REPORTER_HANDOFF.md must point reporters to RETURN_PACKET.md.")
        if return_packet.exists():
            return_text = return_packet.read_text(encoding="utf-8")
            if "NEXT_TASK.md" not in return_text:
                errors.append("RETURN_PACKET.md must point reporters to NEXT_TASK.md.")
            if "USAGE_REPORT_DRAFT.md" not in return_text:
                errors.append("RETURN_PACKET.md must point reporters to USAGE_REPORT_DRAFT.md.")
            if "usage-from-issue" not in return_text:
                errors.append("RETURN_PACKET.md must include the issue lint or preview command.")
            if "not usage proof" not in return_text:
                errors.append("RETURN_PACKET.md must keep the handoff claim boundary explicit.")
        if maintainer_commands.exists():
            command_text = maintainer_commands.read_text(encoding="utf-8")
            if "usage-from-issue" not in command_text or "usage-from-harness" not in command_text:
                errors.append("MAINTAINER_COMMANDS.md must include issue and copied-harness conversion commands.")

    draft = directory / "USAGE_REPORT_DRAFT.md"
    draft_payload = None
    if draft.exists():
        draft_payload = audit_draft(draft, record, args)
        errors.extend(draft_payload["errors"])
        warnings.extend(draft_payload["warnings"])

    return {
        "slug": record["slug"],
        "title": record["title"],
        "directory": display_path(directory),
        "status": "pass" if not errors else "fail",
        "readiness": "reporter-ready" if not errors else "needs-fix",
        "errors": errors,
        "warnings": warnings,
        "files": files,
        "usage_report_draft": draft_payload,
    }


def build_payload(args: argparse.Namespace) -> dict:
    handoff_payload = export_pilot_handoff.build_payload(build_handoff_args(args))
    records = [audit_record(record, args) for record in handoff_payload["records"]]
    errors = []
    if handoff_payload["status"] != "pass":
        errors.append("Pilot handoff source payload failed.")
    for record in records:
        errors.extend(f"{record['slug']}: {error}" for error in record["errors"])
    if not records:
        readiness = "no-active-pilots"
    elif errors:
        readiness = "handoff-audit-failed"
    else:
        readiness = "handoff-audit-ready"
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if not errors else "fail",
        "readiness": readiness,
        "handoff_dir": args.handoff_dir,
        "record_dir": args.record_dir,
        "usage_record_dir": args.usage_record_dir,
        "statuses": handoff_payload["statuses"],
        "slugs": handoff_payload["slugs"],
        "handoff_count": len(records),
        "records": records,
        "errors": errors,
        "warnings": [warning for record in records for warning in record["warnings"]],
        "claim_boundary": (
            "This audit checks whether handoff folders are ready to send; it is not usage proof until a real "
            "task is completed and converted into a validated usage record."
        ),
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Pilot Handoff Audit",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Handoff folders audited: {payload['handoff_count']}",
        f"- Handoff directory: `{payload['handoff_dir']}`",
        f"- Included statuses: {', '.join(payload['statuses'])}",
        "",
        "## Records",
        "",
    ]
    if not payload["records"]:
        lines.append("- none")
        lines.append("")
    for record in payload["records"]:
        draft = record.get("usage_report_draft") or {}
        lines.extend(
            [
                f"### {record['title']} (`{record['slug']}`)",
                "",
                f"- Status: {record['status'].upper()}",
                f"- Readiness: {record['readiness']}",
                f"- Directory: `{record['directory']}`",
                f"- Usage report draft readiness: {draft.get('readiness', 'missing')}",
                "",
            ]
        )
        if record["errors"]:
            lines.append("Errors:")
            lines.extend(f"- {error}" for error in record["errors"])
            lines.append("")
        if record["warnings"]:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in record["warnings"])
            lines.append("")
    lines.extend(["## Claim Boundary", "", payload["claim_boundary"], ""])
    text = "\n".join(lines).rstrip() + "\n"
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit("Refusing to write pilot handoff audit with sensitive text: " + ", ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff-dir", default=export_pilot_handoff.DEFAULT_OUT.as_posix(), help="Pilot handoff folder root")
    parser.add_argument("--record-dir", default=export_pilot_outreach.DEFAULT_RECORD_DIR_TEXT)
    parser.add_argument("--usage-record-dir", default=export_pilot_outreach.DEFAULT_USAGE_RECORD_DIR_TEXT)
    parser.add_argument("--usage-report", default=export_pilot_outreach.DEFAULT_USAGE_REPORT_TEXT)
    parser.add_argument("--pilot-board-report", default=export_pilot_outreach.DEFAULT_PILOT_BOARD_REPORT_TEXT)
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="Pilot handoff audit Markdown path")
    parser.add_argument("--status", action="append", choices=sorted(export_pilot_outreach.pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Pilot handoff audit: {payload['readiness']}")
        print(f"- handoff folders: {payload['handoff_count']}")
        for record in payload["records"]:
            print(f"- {record['slug']}: {record['status']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

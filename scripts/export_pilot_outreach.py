#!/usr/bin/env python3
"""Write privacy-safe outreach copy from prepared pilot-board records."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pilot_board
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_OUTREACH.md"
DEFAULT_RECORD_DIR_TEXT = "Docs/Environment/pilot-records"
DEFAULT_USAGE_RECORD_DIR_TEXT = "Docs/Environment/usage-records"
DEFAULT_USAGE_REPORT_TEXT = "Docs/Environment/USAGE_RECORDS.md"
DEFAULT_PILOT_BOARD_REPORT_TEXT = "Docs/Environment/PILOT_BOARD.md"
DEFAULT_ACTIVE_STATUSES = ("prepared", "invited", "completed")


def display_path(value: str) -> str:
    if not value:
        return "not recorded"
    path = Path(value)
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return value


def selected_records(records: list[dict], statuses: tuple[str, ...], slugs: tuple[str, ...]) -> list[dict]:
    selected = []
    status_set = set(statuses)
    slug_set = set(slugs)
    for record in records:
        if status_set and record.get("status") not in status_set:
            continue
        if slug_set and record.get("slug") not in slug_set:
            continue
        selected.append(record)
    return sorted(selected, key=lambda item: (item.get("selected_index", 999), item.get("slug", "")))


def commands_for(record: dict, args: argparse.Namespace) -> dict:
    slug = record["slug"]
    return {
        "mark_invited": (
            f"codex-harness pilot-update {slug} --status invited "
            f"--record-dir {args.record_dir} --usage-record-dir {args.usage_record_dir} "
            f"--report {args.pilot_board_report} --notes \"sent to reporter\""
        ),
        "mark_completed": (
            f"codex-harness pilot-update {slug} --status completed "
            f"--record-dir {args.record_dir} --usage-record-dir {args.usage_record_dir} "
            f"--report {args.pilot_board_report} --notes \"reporter completed task and shared public-safe evidence\""
        ),
        "lint_issue": (
            "codex-harness usage-from-issue <completed-issue.md> "
            f"--record-dir {args.usage_record_dir} --report {args.usage_report} "
            f"--pilot-record-dir {args.record_dir} --pilot-board-report {args.pilot_board_report} "
            "--lint-only --json"
        ),
        "preview_issue": (
            "codex-harness usage-from-issue <completed-issue.md> "
            f"--record-dir {args.usage_record_dir} --report {args.usage_report} "
            f"--pilot-record-dir {args.record_dir} --pilot-board-report {args.pilot_board_report} "
            "--no-write --json"
        ),
        "convert_issue": (
            "codex-harness usage-from-issue <completed-issue.md> "
            f"--record-dir {args.usage_record_dir} --report {args.usage_report} "
            f"--pilot-record-dir {args.record_dir} --pilot-board-report {args.pilot_board_report} --json"
        ),
        "preview_harness": (
            "codex-harness usage-from-harness <generated-harness> "
            f"--slug {slug} --evidence-type private-summary "
            "--privacy-review \"Reporter confirmed public-safe private-summary evidence only.\" "
            f"--record-dir {args.usage_record_dir} --report {args.usage_report} "
            f"--pilot-record-dir {args.record_dir} --pilot-board-report {args.pilot_board_report} "
            "--no-write --json"
        ),
        "convert_harness": (
            "codex-harness usage-from-harness <generated-harness> "
            f"--slug {slug} --evidence-type private-summary "
            "--privacy-review \"Reporter confirmed public-safe private-summary evidence only.\" "
            f"--record-dir {args.usage_record_dir} --report {args.usage_report} "
            f"--pilot-record-dir {args.record_dir} --pilot-board-report {args.pilot_board_report} --json"
        ),
    }


def reporter_message(record: dict) -> str:
    pilot_pack = display_path(record.get("pilot_pack", ""))
    issue_draft = display_path(record.get("issue_draft", ""))
    return "\n".join(
        [
            f"Would you be willing to try one small real Codex task using {record['title']}?",
            "",
            f"- Domain: {record['domain']}",
            f"- Pilot pack: {pilot_pack}",
            f"- Issue draft: {issue_draft}",
            "",
            "Please pick one privacy-safe task, run the generated harness checks, record the task trial,",
            "and share either the completed issue draft or a private copied harness directory with public-safe evidence.",
            "",
            "Do not include secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.",
            "A private-summary report is fine if the raw evidence cannot be public.",
        ]
    )


def build_payload(args: argparse.Namespace) -> dict:
    board = pilot_board.build_payload(Path(args.record_dir), usage_record_dir=Path(args.usage_record_dir))
    statuses = tuple(args.status or DEFAULT_ACTIVE_STATUSES)
    slugs = tuple(args.slug or ())
    records = selected_records(board["records"], statuses, slugs)
    outreach_records = [
        {
            "slug": record["slug"],
            "title": record["title"],
            "status": record["status"],
            "domain": record["domain"],
            "harness_label": record.get("harness_label") or record["title"],
            "source_type": record["source_type"],
            "generation_path": record["generation_path"],
            "pilot_pack": display_path(record.get("pilot_pack", "")),
            "issue_draft": display_path(record.get("issue_draft", "")),
            "reporter_message": reporter_message(record),
            "commands": commands_for(record, args),
        }
        for record in records
    ]
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": board["status"],
        "readiness": "outreach-ready" if outreach_records else "no-active-pilots",
        "record_dir": args.record_dir,
        "usage_record_dir": args.usage_record_dir,
        "statuses": list(statuses),
        "slugs": list(slugs),
        "outreach_count": len(outreach_records),
        "pilot_board": {
            "status": board["status"],
            "readiness": board["readiness"],
            "summary": board["summary"],
            "errors": board["errors"],
        },
        "records": outreach_records,
        "claim_boundary": (
            "Outreach packets help request and track pilots; they are not usage proof until a real task "
            "is completed and converted into a validated usage record."
        ),
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Pilot Outreach Packet",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Outreach-ready pilots: {payload['outreach_count']}",
        f"- Included statuses: {', '.join(payload['statuses'])}",
        f"- Pilot board readiness: {payload['pilot_board']['readiness']}",
        "",
        "## Outreach Items",
        "",
    ]
    if not payload["records"]:
        lines.append("- none")
        lines.append("")
    for index, record in enumerate(payload["records"], start=1):
        commands = record["commands"]
        lines.extend(
            [
                f"### {index}. {record['title']} (`{record['slug']}`)",
                "",
                f"- Status: `{record['status']}`",
                f"- Domain: {record['domain']}",
                f"- Source type: `{record['source_type']}`",
                f"- Generation path: `{record['generation_path']}`",
                f"- Pilot pack: `{record['pilot_pack']}`",
                f"- Issue draft: `{record['issue_draft']}`",
                "",
                "Reporter message:",
                "",
                "```text",
                record["reporter_message"],
                "```",
                "",
                "Maintainer tracking:",
                "",
                "```bash",
                commands["mark_invited"],
                commands["mark_completed"],
                "```",
                "",
                "Issue-body conversion:",
                "",
                "```bash",
                commands["lint_issue"],
                commands["preview_issue"],
                commands["convert_issue"],
                "```",
                "",
                "Copied-harness conversion:",
                "",
                "```bash",
                commands["preview_harness"],
                commands["convert_harness"],
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "Sending or tracking an invite is not adoption evidence. Count only completed, privacy-reviewed task evidence converted into valid usage records.",
        ]
    )
    text = "\n".join(lines).rstrip() + "\n"
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit("Refusing to write pilot outreach with sensitive text: " + ", ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR_TEXT)
    parser.add_argument("--usage-record-dir", default=DEFAULT_USAGE_RECORD_DIR_TEXT)
    parser.add_argument("--usage-report", default=DEFAULT_USAGE_REPORT_TEXT)
    parser.add_argument("--pilot-board-report", default=DEFAULT_PILOT_BOARD_REPORT_TEXT)
    parser.add_argument("--out", default=DEFAULT_REPORT.as_posix(), help="Pilot outreach Markdown path")
    parser.add_argument("--status", action="append", choices=sorted(pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown outreach packet")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_report(Path(args.out), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Pilot outreach: {payload['readiness']}")
        print(f"- outreach-ready pilots: {payload['outreach_count']}")
        for record in payload["records"]:
            print(f"- {record['slug']}: {record['status']} / {record['domain']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

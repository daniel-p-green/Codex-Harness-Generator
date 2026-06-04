#!/usr/bin/env python3
"""Write reporter completion reply templates for active pilot issues."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import export_pilot_github_issues
import export_pilot_handoff
import export_pilot_outreach
import usage_from_issue
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "Docs" / "Environment" / "pilot-reporter-replies"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_REPORTER_REPLIES.md"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def build_issue_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        record_dir=args.record_dir,
        usage_record_dir=args.usage_record_dir,
        usage_report=args.usage_report,
        pilot_board_report=args.pilot_board_report,
        out_dir=args.out_dir,
        report=args.report,
        status=args.status,
        slug=args.slug,
        label=None,
    )


def reply_markdown(record: dict) -> str:
    return "\n".join(
        [
            f"# Reporter Completion Reply: {record['slug']}",
            "",
            "Copy the Markdown below into a new GitHub issue comment after completing one real, public-safe task with the generated harness.",
            "",
            "Do not include secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, or raw private transcripts.",
            "",
            f"- Pilot: `{record['slug']}`",
            f"- Issue: {record['live_issue_url'] or 'not opened yet'}",
            f"- Domain: {record['domain']}",
            "",
            "## Reply Template",
            "",
            "```markdown",
            record["reporter_reply_template"],
            "```",
            "",
            "## Maintainer Validation",
            "",
            "After the reporter posts this reply, rerun live sync or preview conversion before writing usage evidence:",
            "",
            "```bash",
            record["lint_github_issue"],
            record["preview_github_issue"],
            "```",
            "",
            "This reply is not usage proof until it passes lint and is converted into a validated usage record.",
        ]
    )


def template_sections(template: str) -> dict:
    return usage_from_issue.parse_issue_sections(template)


def build_payload(args: argparse.Namespace) -> dict:
    issue_payload = export_pilot_github_issues.build_payload(build_issue_args(args))
    records = []
    for record in issue_payload["records"]:
        filename = f"{export_pilot_handoff.safe_slug(record['slug'])}-reporter-reply.md"
        reply_path = Path(args.out_dir) / filename
        sections = template_sections(record["reporter_reply_template"])
        records.append(
            {
                "slug": record["slug"],
                "title": record["title"],
                "status": record["status"],
                "domain": record["domain"],
                "issue_url": record["live_issue_url"],
                "reply_file": reply_path.as_posix(),
                "display_reply_file": display_path(reply_path),
                "reply_template": record["reporter_reply_template"],
                "reply_markdown": reply_markdown(record),
                "lint_github_issue": record["lint_github_issue"],
                "preview_github_issue": record["preview_github_issue"],
                "convert_github_issue": record["convert_github_issue"],
                "section_count": len(sections),
                "section_names": sorted(sections),
            }
        )
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": issue_payload["status"],
        "readiness": "reporter-replies-ready" if records else "no-active-pilots",
        "out_dir": args.out_dir,
        "report": args.report,
        "record_dir": args.record_dir,
        "usage_record_dir": args.usage_record_dir,
        "statuses": issue_payload["statuses"],
        "slugs": issue_payload["slugs"],
        "reply_count": len(records),
        "records": records,
        "pilot_board": issue_payload["pilot_board"],
        "claim_boundary": (
            "Reporter reply templates reduce completion friction; they are not usage proof until a real task "
            "is completed, privacy-reviewed, and converted into a validated usage record."
        ),
    }


def safe_write(path: Path, text: str) -> None:
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit(f"Refusing to write sensitive reporter reply text to {path.as_posix()}: {', '.join(findings)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Pilot Reporter Replies",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Reporter reply templates: {payload['reply_count']}",
        f"- Included statuses: {', '.join(payload['statuses'])}",
        f"- Pilot board readiness: {payload['pilot_board']['readiness']}",
        "",
        "## Reply Files",
        "",
    ]
    if not payload["records"]:
        lines.extend(["- none", ""])
    for record in payload["records"]:
        lines.extend(
            [
                f"- `{record['slug']}`: `{record['display_reply_file']}`",
                f"  - Issue: {record['issue_url'] or 'not opened yet'}",
                f"  - Sections: {', '.join(record['section_names'])}",
                f"  - Preview: `{record['preview_github_issue']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Do not count generated reply templates as usage evidence. Count only completed, privacy-reviewed task evidence converted into valid usage records.",
            "",
        ]
    )
    safe_write(path, "\n".join(lines))


def write_outputs(payload: dict) -> None:
    Path(payload["out_dir"]).mkdir(parents=True, exist_ok=True)
    for record in payload["records"]:
        safe_write(Path(record["reply_file"]), record["reply_markdown"])
    write_report(Path(payload["report"]), payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=export_pilot_outreach.DEFAULT_RECORD_DIR_TEXT)
    parser.add_argument("--usage-record-dir", default=export_pilot_outreach.DEFAULT_USAGE_RECORD_DIR_TEXT)
    parser.add_argument("--usage-report", default=export_pilot_outreach.DEFAULT_USAGE_REPORT_TEXT)
    parser.add_argument("--pilot-board-report", default=export_pilot_outreach.DEFAULT_PILOT_BOARD_REPORT_TEXT)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR.as_posix(), help="Directory for reporter reply template files")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="Markdown reporter reply queue report path")
    parser.add_argument("--status", action="append", choices=sorted(export_pilot_outreach.pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--no-write", action="store_true", help="Do not write reply files or report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_outputs(payload)
    if args.json:
        printable = dict(payload)
        printable["records"] = [
            {key: value for key, value in record.items() if key not in ("reply_markdown", "reply_template")}
            for record in payload["records"]
        ]
        print(json.dumps(printable, indent=2))
    else:
        print(f"Pilot reporter replies: {payload['readiness']}")
        print(f"- reply templates: {payload['reply_count']}")
        for record in payload["records"]:
            print(f"- {record['slug']}: {record['display_reply_file']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

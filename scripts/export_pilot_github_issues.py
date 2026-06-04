#!/usr/bin/env python3
"""Write GitHub-ready issue bodies for active pilot-board records."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path

import export_pilot_handoff
import export_pilot_outreach
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "Docs" / "Environment" / "pilot-github-issues"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_GITHUB_ISSUES.md"
GITHUB_ISSUE_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+")


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def reporter_completion_reply_template(record: dict) -> str:
    return "\n".join(
        [
            "### Outcome",
            "",
            "success",
            "",
            "### Public-safe task summary",
            "",
            "Describe one real task you completed with this generated harness. Keep it public-safe.",
            "",
            "### Evidence",
            "",
            "- Evidence item 1: what the harness helped produce, organize, catch, or verify.",
            "- Evidence item 2: another public-safe artifact, workflow improvement, or observed behavior.",
            "",
            "### Verification performed",
            "",
            "- Check 1: command, generated script, review step, or artifact inspection you actually performed.",
            "- Check 2: second check or review that supports the outcome.",
            "",
            "### Privacy review",
            "",
            "This report excludes secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, and raw private transcripts.",
            "",
            "### Limitations",
            "",
            "- This reports one generated harness on one task; it does not prove broad adoption or production readiness.",
        ]
    )


def issue_body_markdown(record: dict, payload: dict) -> str:
    return "\n".join(
        [
            f"# External Usage Pilot: {record['title']}",
            "",
            payload["claim_boundary"],
            "",
            "## Reporter Instructions",
            "",
            record["reporter_message"],
            "",
            "After completing one privacy-safe task, reply to this issue with the completion template below. Maintainers can then run `codex-harness usage-from-github-issue ... --include-comments` without asking you to edit the original issue body.",
            "Keep evidence public-safe: no secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.",
            "",
            "## Reporter Completion Reply Template",
            "",
            "Copy this section into a new issue comment after the pilot task, then replace the guidance text with your public-safe result.",
            "",
            "```markdown",
            reporter_completion_reply_template(record),
            "```",
            "",
            "## Maintainer Preview Commands",
            "",
            "```bash",
            record["commands"]["lint_issue"].replace("<completed-issue.md>", "<this-issue-body.md>"),
            record["commands"]["preview_issue"].replace("<completed-issue.md>", "<this-issue-body.md>"),
            "```",
            "",
            "## Usage Report Body",
            "",
            "### Pilot or usage-record slug",
            "",
            record["slug"],
            "",
            "### Domain or project type",
            "",
            record["domain"],
            "",
            "### Generated harness profile or label",
            "",
            record.get("harness_label") or record["title"],
            "",
            "### Evidence type",
            "",
            "private-summary",
            "",
            "### Source type",
            "",
            record["source_type"],
            "",
            "### Generation path",
            "",
            record["generation_path"],
            "",
            "### Outcome",
            "",
            "_no response_",
            "",
            "### Public-safe task summary",
            "",
            "_no response_",
            "",
            "### Evidence",
            "",
            "_no response_",
            "",
            "### Verification performed",
            "",
            "_no response_",
            "",
            "### Privacy review",
            "",
            "_no response_",
            "",
            "### Limitations",
            "",
            "_no response_",
            "",
        ]
    )


def gh_issue_command(title: str, body_file: str, labels: list[str]) -> str:
    parts = ["gh", "issue", "create", "--title", title, "--body-file", body_file]
    for label in labels:
        parts.extend(["--label", label])
    return " ".join(shlex.quote(part) for part in parts)


def live_issue_url(record: dict) -> str:
    candidates = [str(record.get("notes", ""))]
    for item in record.get("status_history") or []:
        candidates.append(str(item.get("notes", "")))
    for candidate in reversed(candidates):
        match = GITHUB_ISSUE_RE.search(candidate)
        if match:
            return match.group(0)
    return ""


def github_issue_import_commands(issue_selector: str, args: argparse.Namespace) -> dict[str, str]:
    base = (
        f"codex-harness usage-from-github-issue {issue_selector} "
        "--include-comments "
        f"--record-dir {args.usage_record_dir} --report {args.usage_report} "
        f"--pilot-record-dir {args.record_dir} --pilot-board-report {args.pilot_board_report} "
    )
    return {
        "lint_github_issue": base + "--lint-only --json",
        "preview_github_issue": base + "--no-write --json",
        "convert_github_issue": base + "--json",
    }


def build_outreach_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        record_dir=args.record_dir,
        usage_record_dir=args.usage_record_dir,
        usage_report=args.usage_report,
        pilot_board_report=args.pilot_board_report,
        out="",
        status=args.status,
        slug=args.slug,
    )


def build_payload(args: argparse.Namespace) -> dict:
    outreach = export_pilot_outreach.build_payload(build_outreach_args(args))
    labels = list(args.label or [])
    records = []
    for record in outreach["records"]:
        filename = f"{export_pilot_handoff.safe_slug(record['slug'])}-github-issue.md"
        body_path = Path(args.out_dir) / filename
        title = f"External usage pilot: {record['title']}"
        body = issue_body_markdown(record, {"claim_boundary": CLAIM_BOUNDARY})
        issue_url = live_issue_url(record)
        issue_selector = issue_url or "<issue-number-or-url>"
        import_commands = github_issue_import_commands(issue_selector, args)
        records.append(
            {
                "slug": record["slug"],
                "title": title,
                "status": record["status"],
                "domain": record["domain"],
                "source_type": record["source_type"],
                "generation_path": record["generation_path"],
                "body_file": body_path.as_posix(),
                "display_body_file": display_path(body_path),
                "body": body,
                "labels": labels,
                "live_issue_url": issue_url,
                "reporter_reply_template": reporter_completion_reply_template(record),
                "gh_issue_create": gh_issue_command(title, display_path(body_path), labels),
                "mark_invited": record["commands"]["mark_invited"],
                "lint_issue": record["commands"]["lint_issue"].replace("<completed-issue.md>", display_path(body_path)),
                "preview_issue": record["commands"]["preview_issue"].replace("<completed-issue.md>", display_path(body_path)),
                **import_commands,
            }
        )
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": outreach["status"],
        "readiness": "github-issue-ready" if records else "no-active-pilots",
        "out_dir": args.out_dir,
        "report": args.report,
        "record_dir": args.record_dir,
        "usage_record_dir": args.usage_record_dir,
        "statuses": outreach["statuses"],
        "slugs": outreach["slugs"],
        "issue_count": len(records),
        "labels": labels,
        "records": records,
        "pilot_board": outreach["pilot_board"],
        "claim_boundary": CLAIM_BOUNDARY,
    }


CLAIM_BOUNDARY = (
    "GitHub issue drafts help open public pilot intake issues; they are not usage proof until a real task "
    "is completed, privacy-reviewed, and converted into a validated usage record."
)


def safe_write(path: Path, text: str) -> None:
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit(f"Refusing to write sensitive GitHub issue text to {path.as_posix()}: {', '.join(findings)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def write_outputs(payload: dict) -> None:
    out_dir = Path(payload["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    for record in payload["records"]:
        safe_write(Path(record["body_file"]), record["body"])
    write_report(Path(payload["report"]), payload)


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Pilot GitHub Issue Queue",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- GitHub-ready issue bodies: {payload['issue_count']}",
        f"- Included statuses: {', '.join(payload['statuses'])}",
        f"- Pilot board readiness: {payload['pilot_board']['readiness']}",
        "",
        "## Issue Commands",
        "",
    ]
    if not payload["records"]:
        lines.extend(["- none", ""])
    for index, record in enumerate(payload["records"], start=1):
        lines.extend(
            [
                f"### {index}. {record['title']} (`{record['slug']}`)",
                "",
                f"- Status: `{record['status']}`",
                f"- Domain: {record['domain']}",
                f"- Source type: `{record['source_type']}`",
                f"- Generation path: `{record['generation_path']}`",
                f"- Body file: `{record['display_body_file']}`",
                f"- Live issue: {record['live_issue_url'] or 'not opened yet'}",
                "",
            ]
        )
        if record["live_issue_url"]:
            lines.extend(
                [
                    "Public issue is already open. Do not create a duplicate.",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "Create public issue:",
                    "",
                    "```bash",
                    record["gh_issue_create"],
                    "```",
                    "",
                    "Then mark the pilot invited:",
                    "",
                    "```bash",
                    record["mark_invited"],
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "Preview the incomplete issue body before sending if desired:",
                "",
                "```bash",
                record["lint_issue"],
                record["preview_issue"],
                "```",
                "",
                "After the reporter completes the public issue, lint, preview, and convert from GitHub:",
                "",
                "```bash",
                record["lint_github_issue"],
                record["preview_github_issue"],
                record["convert_github_issue"],
                "```",
                "",
                "Reporter completion reply template:",
                "",
                "```markdown",
                record["reporter_reply_template"],
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "Opening an issue or marking a pilot invited is not adoption evidence. Count only completed, privacy-reviewed task evidence converted into valid usage records.",
            "",
        ]
    )
    safe_write(path, "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=export_pilot_outreach.DEFAULT_RECORD_DIR_TEXT)
    parser.add_argument("--usage-record-dir", default=export_pilot_outreach.DEFAULT_USAGE_RECORD_DIR_TEXT)
    parser.add_argument("--usage-report", default=export_pilot_outreach.DEFAULT_USAGE_REPORT_TEXT)
    parser.add_argument("--pilot-board-report", default=export_pilot_outreach.DEFAULT_PILOT_BOARD_REPORT_TEXT)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR.as_posix(), help="Directory for GitHub issue body files")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="Markdown queue report path")
    parser.add_argument("--status", action="append", choices=sorted(export_pilot_outreach.pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--label", action="append", help="Optional GitHub label to include; repeatable")
    parser.add_argument("--no-write", action="store_true", help="Do not write issue bodies or report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_outputs(payload)
    if args.json:
        printable = dict(payload)
        printable["records"] = [{key: value for key, value in record.items() if key != "body"} for record in payload["records"]]
        print(json.dumps(printable, indent=2))
    else:
        print(f"Pilot GitHub issues: {payload['readiness']}")
        print(f"- issue bodies: {payload['issue_count']}")
        for record in payload["records"]:
            print(f"- {record['slug']}: {record['display_body_file']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

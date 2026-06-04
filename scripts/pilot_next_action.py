#!/usr/bin/env python3
"""Summarize the next public pilot action from live GitHub issue readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sync_pilot_github_issues
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_NEXT_ACTION.md"


def display_arg_path(path_text: str) -> str:
    return sync_pilot_github_issues.display_path(Path(path_text))


def first_record(records: list[dict], readiness: str) -> dict | None:
    for record in records:
        if record.get("readiness") == readiness:
            return record
    return None


def first_unposted_followup(records: list[dict]) -> dict | None:
    for record in records:
        if record.get("readiness") == "waiting-for-reporter" and record.get("commands", {}).get("comment_followup"):
            return record
    return None


def sync_command(args: argparse.Namespace) -> str:
    parts = [
        "codex-harness",
        "pilot-github-sync",
        "--record-dir",
        display_arg_path(args.record_dir),
        "--usage-record-dir",
        display_arg_path(args.usage_record_dir),
        "--usage-report",
        display_arg_path(args.usage_report),
        "--pilot-board-report",
        display_arg_path(args.pilot_board_report),
        "--report",
        display_arg_path(args.sync_report),
        "--followup-dir",
        display_arg_path(args.followup_dir),
    ]
    if args.repo:
        parts.extend(["--repo", args.repo])
    if args.gh_bin and args.gh_bin != "gh":
        parts.extend(["--gh-bin", args.gh_bin])
    return " ".join(parts)


def build_next_action(sync_payload: dict, args: argparse.Namespace) -> dict:
    summary = sync_payload["summary"]
    records = sync_payload["records"]

    if sync_payload["status"] != "pass" or summary["needs_attention"]:
        record = first_record(records, "needs-attention")
        return {
            "type": "fix-sync-attention",
            "priority": "high",
            "slug": record.get("slug") if record else "",
            "issue_url": record.get("issue_url") if record else "",
            "command": sync_command(args),
            "reason": "At least one live pilot issue needs maintainer attention before reporter follow-up or conversion.",
        }

    record = first_record(records, "conversion-ready")
    if record:
        return {
            "type": "preview-conversion",
            "priority": "high",
            "slug": record["slug"],
            "issue_url": record["issue_url"],
            "command": record["commands"]["preview"],
            "reason": "A live pilot issue has enough public-safe evidence to preview conversion before writing a usage record.",
        }

    record = first_unposted_followup(records)
    if record:
        reporter_replied_after_followup = record.get("reporter_replies", {}).get("after_latest_maintainer_followup", False)
        return {
            "type": "post-reporter-clarification" if reporter_replied_after_followup else "post-reporter-followup",
            "priority": "high",
            "slug": record["slug"],
            "issue_url": record["issue_url"],
            "followup_file": record["display_followup_file"],
            "maintainer_followup_comment": record.get("maintainer_followup_comment", {}),
            "reporter_replies": record.get("reporter_replies", {}),
            "missing_fields": record["missing_fields"],
            "command": record["commands"]["comment_followup"],
            "reason": (
                "A reporter replied after the latest maintainer follow-up, but required evidence fields are still missing; post a targeted clarification."
                if reporter_replied_after_followup
                else "A live pilot issue is missing public-safe evidence fields; post the generated follow-up comment."
            ),
        }

    record = first_record(records, "waiting-for-reporter")
    if record:
        return {
            "type": "wait-for-reporter-response",
            "priority": "medium",
            "slug": record["slug"],
            "issue_url": record["issue_url"],
            "followup_file": "",
            "maintainer_followup_comment": record.get("maintainer_followup_comment", {}),
            "reporter_replies": record.get("reporter_replies", {}),
            "missing_fields": record["missing_fields"],
            "command": sync_command(args),
            "reason": "A maintainer follow-up is already posted; wait for reporter evidence, then rerun sync.",
        }

    record = first_record(records, "needs-live-issue")
    if record:
        return {
            "type": "record-live-issue-url",
            "priority": "medium",
            "slug": record["slug"],
            "issue_url": "",
            "command": "codex-harness pilot-github-issues",
            "reason": "At least one active pilot has no live GitHub issue URL recorded yet.",
        }

    return {
        "type": "refresh-proof-next",
        "priority": "low",
        "slug": "",
        "issue_url": "",
        "command": "codex-harness proof-next",
        "reason": "No live pilot issue requires action from the current sync selection.",
    }


def build_payload(
    args: argparse.Namespace,
    fetch_issue=sync_pilot_github_issues.usage_from_github_issue.fetch_github_issue,
) -> dict:
    sync_payload = sync_pilot_github_issues.build_payload(args, fetch_issue=fetch_issue)
    action = build_next_action(sync_payload, args)
    return {
        "generated": sync_payload["generated"],
        "status": sync_payload["status"],
        "readiness": sync_payload["readiness"],
        "summary": sync_payload["summary"],
        "next_action": action,
        "waiting_followups": [
            {
                "slug": record["slug"],
                "issue_url": record["issue_url"],
                "followup_file": record["display_followup_file"],
                "missing_fields": record["missing_fields"],
                "command": record["commands"].get("comment_followup", ""),
                "maintainer_followup_posted": record.get("maintainer_followup_posted", False),
                "maintainer_followup_comment": record.get("maintainer_followup_comment", {}),
                "reporter_replies": record.get("reporter_replies", {}),
            }
            for record in sync_payload["records"]
            if record.get("readiness") == "waiting-for-reporter"
        ],
        "conversion_ready": [
            {
                "slug": record["slug"],
                "issue_url": record["issue_url"],
                "preview_command": record["commands"].get("preview", ""),
                "convert_command": record["commands"].get("convert", ""),
            }
            for record in sync_payload["records"]
            if record.get("readiness") == "conversion-ready"
        ],
        "claim_boundary": (
            "This chooses the next public pilot action; it does not prove adoption. "
            "Count only converted, validated usage records as usage evidence."
        ),
    }


def write_report(path: Path, payload: dict) -> None:
    action = payload["next_action"]
    lines = [
        "# Pilot Next Action",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Tracked pilots: {payload['summary']['total']}",
        f"- Conversion-ready issues: {payload['summary']['conversion_ready']}",
        f"- Waiting for reporter: {payload['summary']['waiting_for_reporter']}",
        f"- Maintainer follow-ups already posted: {payload['summary'].get('maintainer_followups_posted', 0)}",
        f"- Reporter replies: {payload['summary'].get('reporter_reply_count', 0)}",
        f"- Reporter replies after latest maintainer follow-up: {payload['summary'].get('reporter_replies_after_followup', 0)}",
        f"- Needs attention: {payload['summary']['needs_attention']}",
        f"- Missing live issue URL: {payload['summary']['missing_issue_url']}",
        "",
        "## Next Action",
        "",
        f"- Type: `{action['type']}`",
        f"- Priority: `{action['priority']}`",
        f"- Pilot: `{action.get('slug') or 'none'}`",
        f"- Issue: {action.get('issue_url') or 'none'}",
        f"- Maintainer follow-up: {action.get('maintainer_followup_comment', {}).get('url') or 'none'}",
        f"- Maintainer follow-up posted at: `{action.get('maintainer_followup_comment', {}).get('created_at') or 'none'}`",
        f"- Latest reporter reply: {action.get('reporter_replies', {}).get('latest', {}).get('url') or 'none'}",
        f"- Reporter replied after latest maintainer follow-up: `{str(action.get('reporter_replies', {}).get('after_latest_maintainer_followup', False)).lower()}`",
        f"- Reason: {action['reason']}",
        "",
        "```bash",
        action["command"],
        "```",
        "",
        "## Waiting Follow-Ups",
        "",
    ]
    if payload["waiting_followups"]:
        for item in payload["waiting_followups"]:
            lines.extend(
                [
                    f"- `{item['slug']}`: {item['issue_url']}",
                    f"  - Follow-up file: `{item['followup_file'] or 'already posted'}`",
                    f"  - Maintainer follow-up already posted: `{str(item.get('maintainer_followup_posted', False)).lower()}`",
                    f"  - Maintainer follow-up URL: {item.get('maintainer_followup_comment', {}).get('url') or 'none'}",
                    f"  - Maintainer follow-up posted at: `{item.get('maintainer_followup_comment', {}).get('created_at') or 'none'}`",
                    f"  - Reporter replies: {item.get('reporter_replies', {}).get('count', 0)}",
                    f"  - Latest reporter reply: {item.get('reporter_replies', {}).get('latest', {}).get('url') or 'none'}",
                    f"  - Reporter replied after latest maintainer follow-up: `{str(item.get('reporter_replies', {}).get('after_latest_maintainer_followup', False)).lower()}`",
                    f"  - Missing fields: {', '.join(item['missing_fields']) if item['missing_fields'] else 'none'}",
                    f"  - Command: `{item['command'] or 'wait for reporter reply, then rerun sync'}`",
                ]
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Conversion Ready", ""])
    if payload["conversion_ready"]:
        for item in payload["conversion_ready"]:
            lines.extend(
                [
                    f"- `{item['slug']}`: {item['issue_url']}",
                    f"  - Preview: `{item['preview_command']}`",
                    f"  - Convert: `{item['convert_command']}`",
                ]
            )
    else:
        lines.append("- none")
    text = "\n".join(lines).rstrip() + "\n"
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit("Refusing to write pilot next action report with sensitive text: " + ", ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=sync_pilot_github_issues.DEFAULT_RECORD_DIR.as_posix(), help="Pilot-board record directory")
    parser.add_argument("--usage-record-dir", default=sync_pilot_github_issues.DEFAULT_USAGE_RECORD_DIR.as_posix(), help="Usage-record JSON directory")
    parser.add_argument("--usage-report", default=sync_pilot_github_issues.DEFAULT_USAGE_REPORT.as_posix(), help="Usage-record Markdown report path")
    parser.add_argument("--pilot-board-report", default=sync_pilot_github_issues.DEFAULT_PILOT_BOARD_REPORT.as_posix(), help="Pilot-board Markdown report path")
    parser.add_argument("--sync-report", default=sync_pilot_github_issues.DEFAULT_REPORT.as_posix(), help="GitHub issue sync Markdown report path")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="Pilot next-action Markdown report path")
    parser.add_argument("--followup-dir", default=sync_pilot_github_issues.DEFAULT_FOLLOWUP_DIR.as_posix(), help="Directory for per-issue reporter follow-up Markdown files")
    parser.add_argument("--repo", help="Optional GitHub repository in owner/name form")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable")
    parser.add_argument("--generated", default=sync_pilot_github_issues.utc_now(), help="UTC timestamp override for previewed records")
    parser.add_argument("--status", action="append", choices=sorted(sync_pilot_github_issues.pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        action = payload["next_action"]
        print(f"Pilot next action: {action['type']}")
        print(f"- pilot: {action.get('slug') or 'none'}")
        print(f"- command: {action['command']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

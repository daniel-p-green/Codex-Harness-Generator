#!/usr/bin/env python3
"""Check live GitHub pilot issues for conversion readiness."""

from __future__ import annotations

import argparse
import json
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import export_pilot_github_issues
import pilot_board
import usage_from_github_issue
from record_usage_case import DEFAULT_RECORD_DIR as DEFAULT_USAGE_RECORD_DIR
from record_usage_case import DEFAULT_REPORT as DEFAULT_USAGE_REPORT
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD_DIR = pilot_board.DEFAULT_RECORD_DIR
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_GITHUB_SYNC.md"
DEFAULT_FOLLOWUP_DIR = REPO_ROOT / "Docs" / "Environment" / "pilot-github-followups"
DEFAULT_PILOT_BOARD_REPORT = pilot_board.DEFAULT_REPORT


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def selected_records(records: list[dict], statuses: tuple[str, ...], slugs: tuple[str, ...]) -> list[dict]:
    status_set = set(statuses)
    slug_set = set(slugs)
    selected = []
    for record in records:
        if status_set and record.get("status") not in status_set:
            continue
        if slug_set and record.get("slug") not in slug_set:
            continue
        selected.append(record)
    return sorted(selected, key=lambda item: (item.get("selected_index", 999), item.get("slug", "")))


def lint_args(args: argparse.Namespace, record: dict, issue_url: str) -> argparse.Namespace:
    return argparse.Namespace(
        issue=issue_url,
        repo=args.repo,
        gh_bin=args.gh_bin,
        include_comments=True,
        slug=record["slug"],
        title=None,
        harness_label=None,
        source_type=None,
        generation_path=None,
        generated=args.generated,
        record_dir=args.usage_record_dir,
        report=args.usage_report,
        pilot_record_dir=args.record_dir,
        pilot_board_report=args.pilot_board_report,
        pilot_notes="converted from synced GitHub issue",
        force=False,
        lint_only=True,
        no_write=False,
        json=True,
    )


def conversion_command(issue_url: str, args: argparse.Namespace, *, lint_only: bool = False, no_write: bool = False) -> str:
    parts = [
        "codex-harness",
        "usage-from-github-issue",
        issue_url,
        "--include-comments",
        "--record-dir",
        args.usage_record_dir,
        "--report",
        args.usage_report,
        "--pilot-record-dir",
        args.record_dir,
        "--pilot-board-report",
        args.pilot_board_report,
    ]
    if args.repo:
        parts.extend(["--repo", args.repo])
    if args.gh_bin and args.gh_bin != "gh":
        parts.extend(["--gh-bin", args.gh_bin])
    if lint_only:
        parts.append("--lint-only")
    if no_write:
        parts.append("--no-write")
    parts.append("--json")
    return " ".join(parts)


def gh_issue_comment_command(issue_url: str, followup_file: str) -> str:
    parts = ["gh", "issue", "comment", issue_url, "--body-file", followup_file]
    return " ".join(shlex.quote(part) for part in parts)


def followup_path(args: argparse.Namespace, record: dict) -> Path:
    return Path(args.followup_dir) / f"{record['slug']}-followup.md"


FIELD_LABELS = {
    "outcome": "Outcome",
    "task_summary": "Public-safe task summary",
    "evidence": "Evidence",
    "verification": "Verification performed",
    "privacy_review": "Privacy review",
    "limitations": "Limitations",
}


FIELD_GUIDANCE = {
    "outcome": "Use `success`, `partial`, `failed`, or `inconclusive`.",
    "task_summary": "Summarize one real task in public-safe terms without private repo names, secrets, personal data, raw logs, or proprietary source.",
    "evidence": "Add at least two public-safe bullets about what the generated harness helped you do or verify.",
    "verification": "Add at least two bullets naming the checks you actually ran or reviews you performed.",
    "privacy_review": "State that the report excludes secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.",
    "limitations": "Add at least one bullet describing the scope limit, such as one task, one repo, one reporter, or incomplete coverage.",
}


def reporter_followup(record: dict) -> str:
    missing = record.get("missing_fields") or []
    if record.get("readiness") == "conversion-ready":
        return "No reporter follow-up needed; this issue is ready for maintainer preview and conversion."
    if record.get("readiness") == "needs-live-issue":
        return "No live GitHub issue URL is recorded for this pilot yet; open or record the issue before following up."
    if record.get("readiness") == "needs-attention":
        return "Maintainer attention needed before reporter follow-up; check the sync errors for this issue."

    lines = [
        "Thanks for taking this on. The issue is not ready to convert into usage evidence yet.",
        "",
        "Please reply with the missing public-safe sections below. Keep the report free of secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.",
        "",
    ]
    fields = missing or ["outcome", "task_summary", "evidence", "verification", "privacy_review", "limitations"]
    for field in fields:
        label = FIELD_LABELS.get(field, field.replace("_", " ").title())
        guidance = FIELD_GUIDANCE.get(field, "Add a public-safe value for this field.")
        lines.extend(
            [
                f"### {label}",
                "",
                f"{guidance}",
                "",
            ]
        )
    lines.append("Once those sections are present, a maintainer can run `codex-harness pilot-github-sync` again and preview conversion.")
    return "\n".join(lines).strip()


def issue_sync_record(
    args: argparse.Namespace,
    record: dict,
    fetch_issue: Callable[..., dict],
) -> dict:
    issue_url = export_pilot_github_issues.live_issue_url(record)
    base = {
        "slug": record["slug"],
        "pilot_status": record["status"],
        "domain": record["domain"],
        "source_type": record["source_type"],
        "generation_path": record["generation_path"],
        "issue_url": issue_url,
        "status": "missing-issue-url",
        "readiness": "needs-live-issue",
        "errors": [],
        "warnings": [],
        "missing_fields": [],
        "counts": {},
        "github_issue": {},
        "commands": {},
        "reporter_followup": "",
        "followup_file": "",
        "display_followup_file": "",
    }
    if not issue_url:
        base["errors"] = ["Pilot record has no live GitHub issue URL in notes or status history."]
        base["reporter_followup"] = reporter_followup(base)
        return base

    base["commands"] = {
        "lint": conversion_command(issue_url, args, lint_only=True),
        "preview": conversion_command(issue_url, args, no_write=True),
        "convert": conversion_command(issue_url, args),
    }
    try:
        github_payload = fetch_issue(issue_url, repo=args.repo or "", gh_bin=args.gh_bin, include_comments=True)
        lint_payload = usage_from_github_issue.build_payload(
            lint_args(args, record, issue_url),
            github_payload=github_payload,
        )
    except SystemExit as exc:
        base["status"] = "fetch-failed"
        base["readiness"] = "needs-attention"
        base["errors"] = [str(exc)]
        base["reporter_followup"] = reporter_followup(base)
        return base

    base["status"] = lint_payload["status"]
    base["readiness"] = "conversion-ready" if lint_payload["status"] == "pass" else "waiting-for-reporter"
    base["errors"] = lint_payload.get("errors", [])
    base["warnings"] = lint_payload.get("warnings", [])
    base["missing_fields"] = lint_payload.get("missing_fields", [])
    base["counts"] = lint_payload.get("counts", {})
    base["github_issue"] = lint_payload.get("github_issue", {})
    base["reporter_followup"] = reporter_followup(base)
    if base["readiness"] == "waiting-for-reporter":
        path = followup_path(args, record)
        base["followup_file"] = path.as_posix()
        base["display_followup_file"] = display_path(path)
        base["commands"]["comment_followup"] = gh_issue_comment_command(issue_url, base["display_followup_file"])
    return base


def summarize(records: list[dict]) -> dict:
    return {
        "total": len(records),
        "live_issue_count": sum(1 for record in records if record.get("issue_url")),
        "conversion_ready": sum(1 for record in records if record.get("readiness") == "conversion-ready"),
        "waiting_for_reporter": sum(1 for record in records if record.get("readiness") == "waiting-for-reporter"),
        "needs_attention": sum(1 for record in records if record.get("readiness") == "needs-attention"),
        "missing_issue_url": sum(1 for record in records if record.get("readiness") == "needs-live-issue"),
    }


def build_payload(args: argparse.Namespace, fetch_issue: Callable[..., dict] = usage_from_github_issue.fetch_github_issue) -> dict:
    board = pilot_board.build_payload(Path(args.record_dir), usage_record_dir=Path(args.usage_record_dir))
    statuses = tuple(args.status or ("invited", "completed"))
    slugs = tuple(args.slug or ())
    records = [
        issue_sync_record(args, record, fetch_issue)
        for record in selected_records(board["records"], statuses, slugs)
    ]
    summary = summarize(records)
    if board["status"] != "pass" or summary["needs_attention"]:
        status = "fail"
    else:
        status = "pass"
    if not records:
        readiness = "no-live-pilots"
    elif summary["conversion_ready"]:
        readiness = "conversion-ready"
    elif summary["waiting_for_reporter"] or summary["missing_issue_url"]:
        readiness = "waiting-for-reporters"
    else:
        readiness = "needs-attention"
    return {
        "generated": utc_now(),
        "status": status,
        "readiness": readiness,
        "record_dir": args.record_dir,
        "usage_record_dir": args.usage_record_dir,
        "followup_dir": args.followup_dir,
        "statuses": list(statuses),
        "slugs": list(slugs),
        "summary": summary,
        "pilot_board": {
            "status": board["status"],
            "readiness": board["readiness"],
            "summary": board["summary"],
            "errors": board["errors"],
        },
        "records": records,
        "claim_boundary": (
            "Pilot GitHub issue sync checks public intake readiness only; it is not usage proof until "
            "completed evidence is converted into a validated usage record."
        ),
    }


def safe_write(path: Path, text: str, *, label: str) -> None:
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit(f"Refusing to write {label} with sensitive text: " + ", ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_followups(payload: dict) -> None:
    for record in payload["records"]:
        if record.get("followup_file") and record.get("reporter_followup"):
            safe_write(Path(record["followup_file"]), record["reporter_followup"], label=f"GitHub issue follow-up for {record['slug']}")


def write_report(path: Path, payload: dict) -> None:
    summary = payload["summary"]
    lines = [
        "# Pilot GitHub Issue Sync",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Tracked pilots: {summary['total']}",
        f"- Live issue URLs: {summary['live_issue_count']}",
        f"- Conversion-ready issues: {summary['conversion_ready']}",
        f"- Waiting for reporter: {summary['waiting_for_reporter']}",
        f"- Needs attention: {summary['needs_attention']}",
        f"- Missing live issue URL: {summary['missing_issue_url']}",
        "",
        "## Issue Readiness",
        "",
    ]
    if not payload["records"]:
        lines.extend(["- none", ""])
    for record in payload["records"]:
        lines.extend(
            [
                f"### {record['slug']}",
                "",
                f"- Pilot status: `{record['pilot_status']}`",
                f"- Readiness: `{record['readiness']}`",
                f"- Issue: {record['issue_url'] or 'not recorded'}",
                f"- GitHub state: `{record.get('github_issue', {}).get('state', 'unknown')}`",
                f"- Comments included: {record.get('github_issue', {}).get('comment_count', 0)}",
                f"- Missing fields: {', '.join(record['missing_fields']) if record['missing_fields'] else 'none'}",
                f"- Follow-up file: `{record['display_followup_file']}`" if record.get("display_followup_file") else "- Follow-up file: not needed",
            ]
        )
        if record["errors"]:
            lines.extend(["", "Errors:"])
            lines.extend(f"- {error}" for error in record["errors"])
        if record["warnings"]:
            lines.extend(["", "Warnings:"])
            lines.extend(f"- {warning}" for warning in record["warnings"])
        if record["commands"]:
            lines.extend(
                [
                    "",
                    "Commands:",
                    "",
                    "```bash",
                    record["commands"]["lint"],
                    record["commands"]["preview"],
                    record["commands"]["convert"],
                    *([record["commands"]["comment_followup"]] if record["commands"].get("comment_followup") else []),
                    "```",
                ]
            )
        if record["reporter_followup"]:
            lines.extend(
                [
                    "",
                    "Reporter follow-up:",
                    "",
                    "```markdown",
                    record["reporter_followup"],
                    "```",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "Do not count live issues, comments, or passing lint as adoption proof. Count only converted, validated usage records.",
            "",
        ]
    )
    text = "\n".join(lines).rstrip() + "\n"
    safe_write(path, text, label="GitHub issue sync report")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix(), help="Pilot-board record directory")
    parser.add_argument("--usage-record-dir", default=DEFAULT_USAGE_RECORD_DIR.as_posix(), help="Usage-record JSON directory")
    parser.add_argument("--usage-report", default=DEFAULT_USAGE_REPORT.as_posix(), help="Usage-record Markdown report path")
    parser.add_argument("--pilot-board-report", default=DEFAULT_PILOT_BOARD_REPORT.as_posix(), help="Pilot-board Markdown report path")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="GitHub issue sync report path")
    parser.add_argument("--followup-dir", default=DEFAULT_FOLLOWUP_DIR.as_posix(), help="Directory for per-issue reporter follow-up Markdown files")
    parser.add_argument("--repo", help="Optional GitHub repository in owner/name form")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable")
    parser.add_argument("--generated", default=utc_now(), help="UTC timestamp override for previewed records")
    parser.add_argument("--status", action="append", choices=sorted(pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_followups(payload)
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Pilot GitHub sync: {payload['readiness']}")
        print(f"- tracked pilots: {payload['summary']['total']}")
        print(f"- conversion-ready: {payload['summary']['conversion_ready']}")
        print(f"- waiting: {payload['summary']['waiting_for_reporter']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

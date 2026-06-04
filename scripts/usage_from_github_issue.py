#!/usr/bin/env python3
"""Create usage evidence from a GitHub issue body fetched with gh."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pilot_board
import usage_from_issue
from record_usage_case import (
    ALLOWED_GENERATION_PATHS,
    ALLOWED_SOURCE_TYPES,
    DEFAULT_RECORD_DIR,
    DEFAULT_REPORT,
    display_path,
    find_sensitive_text,
    load_records,
    validate_record,
    write_record,
    write_report,
)


MAINTAINER_FOLLOWUP_MARKER = "<!-- codex-harness-maintainer-followup -->"
USAGE_LINT_MARKER = "<!-- codex-harness-usage-lint -->"


def fetch_github_issue(issue: str, repo: str = "", gh_bin: str = "gh", *, include_comments: bool = False) -> dict:
    fields = "body,title,url,number,state"
    if include_comments:
        fields += ",comments"
    command = [gh_bin, "issue", "view", issue, "--json", fields]
    if repo:
        command.extend(["--repo", repo])
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"gh executable not found: {gh_bin}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise SystemExit(f"gh issue view failed: {detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"gh issue view returned invalid JSON: {exc}") from exc
    if not combined_issue_body(payload, include_comments=include_comments).strip():
        raise SystemExit("GitHub issue body is empty.")
    return payload


def comment_bodies(payload: dict) -> list[str]:
    bodies = []
    for comment in payload.get("comments") or []:
        body = str(comment.get("body", "")).strip()
        if MAINTAINER_FOLLOWUP_MARKER in body or USAGE_LINT_MARKER in body:
            continue
        if body:
            bodies.append(body)
    return bodies


def combined_issue_body(payload: dict, *, include_comments: bool) -> str:
    parts = [str(payload.get("body", "")).strip()]
    if include_comments:
        parts.extend(comment_bodies(payload))
    return "\n\n".join(part for part in parts if part)


def importer_args(args: argparse.Namespace, body: str) -> argparse.Namespace:
    return argparse.Namespace(
        issue_body="-",
        slug=args.slug,
        title=args.title,
        harness_label=args.harness_label,
        source_type=args.source_type,
        generation_path=args.generation_path,
        generated=args.generated,
        record_dir=args.record_dir,
        report=args.report,
        pilot_record_dir=args.pilot_record_dir,
        pilot_board_report=args.pilot_board_report,
        pilot_notes=args.pilot_notes,
        force=args.force,
        lint_only=args.lint_only,
        no_write=args.no_write,
        json=args.json,
        _issue_body_text=body,
    )


def issue_metadata(payload: dict, *, include_comments: bool) -> dict:
    return {
        "number": payload.get("number"),
        "title": payload.get("title", ""),
        "url": payload.get("url", ""),
        "state": payload.get("state", ""),
        "comments_included": include_comments,
        "comment_count": len(comment_bodies(payload)) if include_comments else 0,
    }


def build_payload(args: argparse.Namespace, github_payload: dict | None = None) -> dict:
    github_payload = github_payload or fetch_github_issue(
        args.issue,
        repo=args.repo or "",
        gh_bin=args.gh_bin,
        include_comments=args.include_comments,
    )
    body = combined_issue_body(github_payload, include_comments=args.include_comments)
    sensitive_findings = find_sensitive_text(body)
    converted_args = importer_args(args, body)
    usage_from_issue.resolve_slug(converted_args, required=not args.lint_only)
    usage_from_issue.apply_pilot_defaults(converted_args)
    usage_from_issue.apply_standalone_defaults(converted_args)

    github = issue_metadata(github_payload, include_comments=args.include_comments)
    if args.lint_only:
        lint_payload = usage_from_issue.lint_issue_payload(converted_args)
        if sensitive_findings:
            lint_payload["errors"].append("Sensitive text detected in full GitHub issue body: " + ", ".join(sensitive_findings))
            lint_payload["status"] = "fail"
            lint_payload["readiness"] = "needs-input"
        lint_payload["github_issue"] = github
        return lint_payload

    if sensitive_findings:
        raise SystemExit("Sensitive text detected in full GitHub issue body: " + ", ".join(sensitive_findings))
    usage_from_issue.require_metadata(converted_args)
    record = usage_from_issue.build_record(converted_args)
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
    if not args.no_write:
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

    return {
        "status": "pass",
        "written": not args.no_write,
        "path": display_path(path) if path is not None else None,
        "record": record.to_dict(),
        "pilot_update": pilot_update,
        "github_issue": github,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("issue", help="GitHub issue number, URL, or branch-style issue selector accepted by gh")
    parser.add_argument("--repo", help="Optional GitHub repository in owner/name form")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable")
    parser.add_argument(
        "--include-comments",
        action="store_true",
        help="Include issue comments when linting or converting; later repeated fields override the issue body",
    )
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
    parser.add_argument("--pilot-notes", default="converted from GitHub issue")
    parser.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    parser.add_argument("--lint-only", action="store_true", help="Check GitHub issue-body readiness without building or writing a usage record")
    parser.add_argument("--no-write", action="store_true", help="Validate and preview the record without writing files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    elif args.lint_only:
        print(f"GitHub issue evidence lint: {payload['readiness']}")
        for error in payload["errors"]:
            print(f"- error: {error}")
        for warning in payload["warnings"]:
            print(f"- warning: {warning}")
    elif args.no_write:
        print(f"Validated usage evidence from GitHub issue without writing: {payload['record']['slug']}")
    else:
        print(f"Recorded usage evidence from GitHub issue: {payload['path']}")
        if payload["pilot_update"]:
            print(f"Converted pilot board record: {display_path(Path(payload['pilot_update']['path']))}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

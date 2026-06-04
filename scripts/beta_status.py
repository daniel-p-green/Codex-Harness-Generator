#!/usr/bin/env python3
"""Summarize beta-exit evidence, live pilot queue state, and next action."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import doctor
import pilot_next_action
import sync_pilot_github_issues
import usage_gaps


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "BETA_STATUS.md"
DEFAULT_RECORD_DIR = "Docs/Environment/usage-records"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def command_list(args: argparse.Namespace, next_action: dict) -> list[dict]:
    commands = [
        {
            "name": "next live pilot action",
            "command": next_action.get("command", ""),
            "purpose": next_action.get("reason", "Run the selected next pilot action."),
        },
        {
            "name": "refresh live pilot sync",
            "command": (
                "codex-harness pilot-github-sync "
                f"--record-dir {args.pilot_record_dir} "
                f"--usage-record-dir {args.record_dir} "
                f"--usage-report {args.usage_report} "
                f"--pilot-board-report {args.pilot_board_report} "
                f"--report {args.pilot_github_sync_report} "
                f"--followup-dir {args.followup_dir}"
                + (f" --repo {args.repo}" if args.repo else "")
            ),
            "purpose": "refresh public pilot issue state before converting reporter evidence.",
        },
        {
            "name": "refresh usage gaps",
            "command": f"codex-harness usage-gaps --record-dir {args.record_dir}",
            "purpose": "refresh the evidence thresholds before changing beta-readiness claims.",
        },
        {
            "name": "refresh proof next",
            "command": (
                "codex-harness proof-next "
                f"--record-dir {args.record_dir} "
                f"--pilot-record-dir {args.pilot_record_dir} "
                f"--pilot-board-report {args.pilot_board_report} "
                f"--usage-report {args.usage_report} "
                f"--pilot-github-sync-report {args.pilot_github_sync_report} "
                f"--pilot-github-followup-dir {args.followup_dir}"
            ),
            "purpose": "refresh the ordered beta-exit evidence collection checklist.",
        },
        {
            "name": "strict beta-exit doctor",
            "command": f"codex-harness doctor --beta-exit --record-dir {args.record_dir}",
            "purpose": "apply the roadmap usage-evidence thresholds before treating the repo as beta-exit ready.",
        },
    ]
    return [item for item in commands if item["command"]]


def build_pilot_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        record_dir=args.pilot_record_dir,
        usage_record_dir=args.record_dir,
        usage_report=args.usage_report,
        pilot_board_report=args.pilot_board_report,
        sync_report=args.pilot_github_sync_report,
        report=args.pilot_next_action_report,
        followup_dir=args.followup_dir,
        repo=args.repo,
        gh_bin=args.gh_bin,
        generated=args.generated,
        reminder_after_hours=args.reminder_after_hours,
        status=args.status,
        slug=args.slug,
        no_write=True,
        json=True,
    )


def build_payload(
    args: argparse.Namespace,
    fetch_issue=sync_pilot_github_issues.usage_from_github_issue.fetch_github_issue,
) -> dict:
    generated = args.generated or utc_now()
    gaps_payload = usage_gaps.build_payload(
        Path(args.record_dir),
        min_records=args.min_records,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    pilot_args = build_pilot_args(args)
    pilot_args.generated = generated
    pilot_payload = pilot_next_action.build_payload(pilot_args, fetch_issue=fetch_issue)
    doctor_payload = doctor.build_payload(record_dir=Path(args.record_dir), beta_exit=True)
    beta_exit_ready = (
        gaps_payload.get("readiness") == "beta-exit-evidence-ready"
        and doctor_payload.get("status") == "pass"
    )
    status = "pass" if gaps_payload["status"] == "pass" and pilot_payload["status"] == "pass" else "fail"
    return {
        "generated": generated,
        "status": status,
        "readiness": "beta-exit-ready-for-final-proof" if beta_exit_ready else gaps_payload["readiness"],
        "beta_exit_ready": beta_exit_ready,
        "usage_summary": gaps_payload["summary"],
        "usage_gaps": gaps_payload["gaps"],
        "coverage_projection": gaps_payload["coverage_projection"],
        "pilot_readiness": pilot_payload["readiness"],
        "pilot_summary": pilot_payload["summary"],
        "operator_queue": pilot_payload["operator_queue"],
        "waiting_followups": pilot_payload.get("waiting_followups", []),
        "conversion_ready": pilot_payload.get("conversion_ready", []),
        "next_action": pilot_payload["next_action"],
        "doctor": {
            "status": doctor_payload["status"],
            "readiness": doctor_payload["readiness"],
            "usage_records": next(
                check for check in doctor_payload["checks"] if check["name"] == "usage_records"
            ),
        },
        "commands": command_list(args, pilot_payload["next_action"]),
        "claim_boundary": (
            "This status report is an operator dashboard. It is not usage proof; only converted, "
            "validated usage records count toward beta exit."
        ),
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Beta Status",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Evidence Gap",
        "",
        f"- Usage records: {payload['usage_summary']['total']} total; {payload['usage_gaps']['records']} still needed",
        f"- External or multi-project records: {payload['usage_summary']['external_or_multi_project']} current; {payload['usage_gaps']['external_or_multi_project']} still needed",
        f"- Distinct domains: {payload['usage_summary']['distinct_domains']} current; {payload['usage_gaps']['domains']} still needed",
        f"- Installed brief-based generation records: {payload['usage_summary']['installed_brief_generation']} current; {payload['usage_gaps']['installed_init_brief']} still needed",
        "",
        "## Pilot Queue",
        "",
        f"- Pilot readiness: {payload['pilot_readiness']}",
        f"- Live issues: {payload['pilot_summary']['live_issue_count']}",
        f"- Waiting for reporter: {payload['pilot_summary']['waiting_for_reporter']}",
        f"- Conversion ready: {payload['pilot_summary']['conversion_ready']}",
        f"- Reporter replies: {payload['pilot_summary']['reporter_reply_count']}",
        f"- Stale follow-ups: {payload['pilot_summary'].get('stale_maintainer_followups', 0)}",
        f"- Next reminder review: `{payload['operator_queue']['next_review_at'] or 'none'}`",
        "",
        "Missing fields across waiting issues:",
        "",
    ]
    if payload["operator_queue"]["missing_field_counts"]:
        lines.extend(
            f"- `{field}`: {count}"
            for field, count in payload["operator_queue"]["missing_field_counts"].items()
        )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Waiting Issues",
            "",
        ]
    )
    if payload["waiting_followups"]:
        for item in payload["waiting_followups"]:
            reporter_replies = item.get("reporter_replies", {})
            maintainer_comment = item.get("maintainer_followup_comment", {})
            lines.extend(
                [
                    f"### {item['slug']}",
                    "",
                    f"- Issue: {item.get('issue_url') or 'none'}",
                    f"- Missing fields: {', '.join(item.get('missing_fields', [])) or 'none'}",
                    f"- Reporter replies: {reporter_replies.get('count', 0)}",
                    f"- Reminder due: `{str(item.get('reminder_due', False)).lower()}`",
                    f"- Next reminder at: `{item.get('next_reminder_at') or 'none'}`",
                    f"- Maintainer follow-up posted: `{str(item.get('maintainer_followup_posted', False)).lower()}`",
                    f"- Maintainer follow-up: {maintainer_comment.get('url') or 'none'}",
                    f"- Follow-up file: `{item.get('followup_file') or 'none'}`",
                    "",
                ]
            )
    else:
        lines.append("- none")
        lines.append("")
    lines.extend(
        [
            "## Conversion Ready Issues",
            "",
        ]
    )
    if payload["conversion_ready"]:
        for item in payload["conversion_ready"]:
            lines.extend(
                [
                    f"### {item['slug']}",
                    "",
                    f"- Issue: {item.get('issue_url') or 'none'}",
                    "",
                    "Preview before writing:",
                    "",
                    "```bash",
                    item.get("preview_command", ""),
                    "```",
                    "",
                    "Convert after preview passes:",
                    "",
                    "```bash",
                    item.get("convert_command", ""),
                    "```",
                    "",
                ]
            )
    else:
        lines.append("- none")
    action = payload["next_action"]
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            f"- Type: `{action['type']}`",
            f"- Priority: `{action['priority']}`",
            f"- Pilot: `{action.get('slug') or 'none'}`",
            f"- Issue: {action.get('issue_url') or 'none'}",
            f"- Reason: {action['reason']}",
            "",
            "```bash",
            action["command"],
            "```",
            "",
            "## Commands",
            "",
        ]
    )
    for item in payload["commands"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                item["purpose"],
                "",
                "```bash",
                item["command"],
                "```",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR)
    parser.add_argument("--pilot-record-dir", default="Docs/Environment/pilot-records")
    parser.add_argument("--usage-report", default="Docs/Environment/USAGE_RECORDS.md")
    parser.add_argument("--pilot-board-report", default="Docs/Environment/PILOT_BOARD.md")
    parser.add_argument("--pilot-github-sync-report", default="Docs/Environment/PILOT_GITHUB_SYNC.md")
    parser.add_argument("--pilot-next-action-report", default="Docs/Environment/PILOT_NEXT_ACTION.md")
    parser.add_argument("--followup-dir", default="Docs/Environment/pilot-github-followups")
    parser.add_argument("--repo", help="GitHub repo owner/name for live issue fetches")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable")
    parser.add_argument("--generated", help="UTC timestamp override")
    parser.add_argument("--reminder-after-hours", type=float, default=sync_pilot_github_issues.DEFAULT_REMINDER_AFTER_HOURS)
    parser.add_argument("--status", choices=["completed", "converted", "dropped", "invited", "prepared"], action="append")
    parser.add_argument("--slug", action="append")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--min-records", type=int, default=usage_gaps.DEFAULT_TARGETS["min_records"])
    parser.add_argument("--min-external-or-multi-project", type=int, default=usage_gaps.DEFAULT_TARGETS["min_external_or_multi_project"])
    parser.add_argument("--min-domains", type=int, default=usage_gaps.DEFAULT_TARGETS["min_domains"])
    parser.add_argument("--min-installed-init-brief", type=int, default=usage_gaps.DEFAULT_TARGETS["min_installed_init_brief"])
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown status report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args(argv)

    payload = build_payload(args)
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Beta status: {payload['readiness']}")
        print(f"- next action: {payload['next_action']['type']}")
        print(f"- usage gaps: {payload['usage_gaps']}")
        print(f"- pilot queue: {payload['operator_queue']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

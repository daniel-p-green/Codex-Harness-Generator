#!/usr/bin/env python3
"""Write the next proof actions from current beta-exit gaps."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pilot_board
from record_usage_case import find_sensitive_text
from usage_gaps import DEFAULT_TARGETS, build_payload as build_usage_gap_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PROOF_NEXT.md"
DEFAULT_RECORD_DIR_TEXT = "Docs/Environment/usage-records"
DEFAULT_PILOT_RECORD_DIR_TEXT = "Docs/Environment/pilot-records"
DEFAULT_PILOT_BOARD_REPORT_TEXT = "Docs/Environment/PILOT_BOARD.md"
DEFAULT_USAGE_REPORT_TEXT = "Docs/Environment/USAGE_RECORDS.md"
DEFAULT_PILOT_HANDOFF_OUT_TEXT = "Docs/Environment/pilot-handoffs"
DEFAULT_PILOT_GITHUB_ISSUES_OUT_TEXT = "Docs/Environment/pilot-github-issues"
DEFAULT_PILOT_GITHUB_ISSUES_REPORT_TEXT = "Docs/Environment/PILOT_GITHUB_ISSUES.md"
DEFAULT_PILOT_GITHUB_SYNC_REPORT_TEXT = "Docs/Environment/PILOT_GITHUB_SYNC.md"
GITHUB_ISSUE_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+")


def build_prepare_next_command(pilot: dict, args: argparse.Namespace) -> str:
    target = args.target or pilot["target"]
    parts = [
        "codex-harness",
        "prepare-next-pilot",
        target,
        "--record-dir",
        args.record_dir,
        "--pilot-record-dir",
        args.pilot_record_dir,
        "--out",
        args.pilot_pack_out,
        "--issue-out",
        args.issue_out,
        "--force",
    ]
    return " ".join(parts)


def quoted(value: object) -> str:
    return json.dumps(str(value))


def pilot_value(pilot: dict, key: str, fallback: str = "") -> str:
    value = pilot.get(key)
    if value is None:
        return fallback
    return str(value)


def live_issue_selector(pilot: dict) -> str:
    candidates = [str(pilot.get("notes", ""))]
    for item in pilot.get("status_history") or []:
        candidates.append(str(item.get("notes", "")))
    for candidate in reversed(candidates):
        match = GITHUB_ISSUE_RE.search(candidate)
        if match:
            return match.group(0)
    return "<issue-number-or-url>"


def build_usage_from_harness_command(pilot: dict, args: argparse.Namespace, *, no_write: bool) -> str:
    parts = [
        "codex-harness",
        "usage-from-harness",
        "<generated-harness>",
        "--slug",
        pilot_value(pilot, "slug"),
        "--evidence-type",
        "private-summary",
        "--privacy-review",
        quoted("Reporter confirmed public-safe private-summary evidence only."),
        "--record-dir",
        args.record_dir,
        "--report",
        args.usage_report,
        "--pilot-record-dir",
        args.pilot_record_dir,
        "--pilot-board-report",
        args.pilot_board_report,
    ]
    if no_write:
        parts.append("--no-write")
    parts.append("--json")
    return " ".join(parts)


def build_usage_from_issue_command(pilot: dict, args: argparse.Namespace, *, lint_only: bool = False, no_write: bool = False) -> str:
    parts = [
        "codex-harness",
        "usage-from-issue",
        "<completed-issue.md>",
        "--record-dir",
        args.record_dir,
        "--report",
        args.usage_report,
        "--pilot-record-dir",
        args.pilot_record_dir,
        "--pilot-board-report",
        args.pilot_board_report,
    ]
    if lint_only:
        parts.append("--lint-only")
    if no_write:
        parts.append("--no-write")
    parts.append("--json")
    return " ".join(parts)


def build_conversion_commands(pilot: dict, args: argparse.Namespace) -> list[dict]:
    issue_selector = live_issue_selector(pilot)
    return [
        {
            "name": "preview copied-harness evidence",
            "command": build_usage_from_harness_command(pilot, args, no_write=True),
            "purpose": (
                "validate the generated harness's local eval and task-trial evidence without writing a usage record "
                "or mutating the pilot board"
            ),
        },
        {
            "name": "convert copied-harness evidence",
            "command": build_usage_from_harness_command(pilot, args, no_write=False),
            "purpose": "write the checked usage record and convert the matching pilot after preview output is reviewed",
        },
        {
            "name": "lint issue evidence",
            "command": build_usage_from_issue_command(pilot, args, lint_only=True),
            "purpose": "show missing fields, weak evidence counts, and privacy problems before attempting conversion",
        },
        {
            "name": "preview issue evidence",
            "command": build_usage_from_issue_command(pilot, args, no_write=True),
            "purpose": (
                "validate a completed reporter issue body without writing a usage record or mutating the pilot board"
            ),
        },
        {
            "name": "convert issue evidence",
            "command": build_usage_from_issue_command(pilot, args, no_write=False),
            "purpose": "write the checked usage record and convert the matching pilot after preview output is reviewed",
        },
        {
            "name": "lint GitHub issue evidence",
            "command": (
                f"codex-harness usage-from-github-issue {issue_selector} "
                "--include-comments "
                f"--record-dir {args.record_dir} "
                f"--report {args.usage_report} "
                f"--pilot-record-dir {args.pilot_record_dir} "
                f"--pilot-board-report {args.pilot_board_report} "
                "--lint-only --json"
            ),
            "purpose": "lint a completed public GitHub pilot issue without copying its body into a local file first",
        },
        {
            "name": "convert GitHub issue evidence",
            "command": (
                f"codex-harness usage-from-github-issue {issue_selector} "
                "--include-comments "
                f"--record-dir {args.record_dir} "
                f"--report {args.usage_report} "
                f"--pilot-record-dir {args.pilot_record_dir} "
                f"--pilot-board-report {args.pilot_board_report} "
                "--json"
            ),
            "purpose": "fetch a completed public GitHub pilot issue, write the checked usage record, and convert the matching pilot",
        },
    ]


def build_pilot_handoff_command(args: argparse.Namespace) -> str:
    return (
        "codex-harness pilot-handoff "
        f"--record-dir {args.pilot_record_dir} "
        f"--usage-record-dir {args.record_dir} "
        f"--usage-report {args.usage_report} "
        f"--pilot-board-report {args.pilot_board_report} "
        f"--out {args.pilot_handoff_out} "
        "--force"
    )


def build_pilot_handoff_audit_command(args: argparse.Namespace) -> str:
    return (
        "codex-harness pilot-handoff-audit "
        f"--handoff-dir {args.pilot_handoff_out} "
        f"--record-dir {args.pilot_record_dir} "
        f"--usage-record-dir {args.record_dir} "
        f"--usage-report {args.usage_report} "
        f"--pilot-board-report {args.pilot_board_report}"
    )


def build_pilot_github_issues_command(args: argparse.Namespace) -> str:
    return (
        "codex-harness pilot-github-issues "
        f"--record-dir {args.pilot_record_dir} "
        f"--usage-record-dir {args.record_dir} "
        f"--usage-report {args.usage_report} "
        f"--pilot-board-report {args.pilot_board_report} "
        f"--out-dir {args.pilot_github_issues_out} "
        f"--report {args.pilot_github_issues_report}"
    )


def build_pilot_github_sync_command(args: argparse.Namespace) -> str:
    return (
        "codex-harness pilot-github-sync "
        f"--record-dir {args.pilot_record_dir} "
        f"--usage-record-dir {args.record_dir} "
        f"--usage-report {args.usage_report} "
        f"--pilot-board-report {args.pilot_board_report} "
        f"--report {args.pilot_github_sync_report}"
    )


def active_pilot_for_next(gaps_payload: dict, board_payload: dict) -> dict | None:
    next_pilot = (gaps_payload.get("suggested_pilots") or [None])[0]
    if not next_pilot:
        return None
    slug = next_pilot["slug"]
    active_statuses = {"completed", "invited", "prepared"}
    for record in board_payload.get("records", []):
        if record.get("slug") == slug and record.get("status") in active_statuses:
            return record
    return None


def build_command_sequence(gaps_payload: dict, active_pilot: dict | None, args: argparse.Namespace) -> list[dict]:
    pilots = gaps_payload.get("suggested_pilots", [])
    commands = [
        {
            "name": "refresh gaps",
            "command": f"codex-harness usage-gaps --record-dir {args.record_dir}",
            "purpose": "confirm the beta-exit usage gap before preparing more outreach",
        }
    ]
    if len(pilots) > 1:
        commands.append(
            {
                "name": "preview pilot batch",
                "command": (
                    "codex-harness prepare-pilot-batch "
                    f"--record-dir {args.record_dir} "
                    "--target-root /tmp/codex-beta-exit-pilots "
                    f"--pilot-record-dir {args.pilot_record_dir} "
                    "--dry-run"
                ),
                "purpose": "preview the full suggested pilot batch before deciding whether to prepare every candidate",
            }
        )
    if active_pilot:
        commands.append(
            {
                "name": "review active pilot",
                "command": (
                    "codex-harness pilot-board "
                    f"--record-dir {args.pilot_record_dir} "
                    f"--usage-record-dir {args.record_dir} "
                    f"--report {args.pilot_board_report}"
                ),
                "purpose": "continue the already prepared pilot instead of preparing a duplicate",
            }
        )
        commands.append(
            {
                "name": "export pilot outreach",
                "command": (
                    "codex-harness pilot-outreach "
                    f"--record-dir {args.pilot_record_dir} "
                    f"--usage-record-dir {args.record_dir} "
                    f"--usage-report {args.usage_report} "
                    f"--pilot-board-report {args.pilot_board_report}"
                ),
                "purpose": "write reporter-ready outreach copy and maintainer tracking commands for active pilots",
            }
        )
        commands.append(
            {
                "name": "export pilot handoff",
                "command": build_pilot_handoff_command(args),
                "purpose": "write shareable per-pilot folders with reporter materials and maintainer commands",
            }
        )
        commands.append(
            {
                "name": "audit pilot handoff",
                "command": build_pilot_handoff_audit_command(args),
                "purpose": "verify each handoff folder has reporter materials and an importer-shaped usage draft",
            }
        )
        commands.append(
            {
                "name": "export pilot GitHub issue queue",
                "command": build_pilot_github_issues_command(args),
                "purpose": "write public GitHub issue bodies and gh issue create commands for active pilots",
            }
        )
        commands.append(
            {
                "name": "sync pilot GitHub issue readiness",
                "command": build_pilot_github_sync_command(args),
                "purpose": "fetch live pilot issues and identify which reporter updates are ready to convert",
            }
        )
        if active_pilot["status"] == "prepared":
            commands.append(
                {
                    "name": "mark pilot invited",
                    "command": (
                        f"codex-harness pilot-update {active_pilot['slug']} "
                        "--status invited "
                        f"--record-dir {args.pilot_record_dir} "
                        f"--usage-record-dir {args.record_dir} "
                        f"--report {args.pilot_board_report} "
                        "--notes \"sent to reporter\""
                    ),
                    "purpose": "record outreach after the pilot pack is sent to a reporter",
                }
            )
        if active_pilot["status"] in {"prepared", "invited"}:
            commands.append(
                {
                    "name": "mark pilot completed",
                    "command": (
                        f"codex-harness pilot-update {active_pilot['slug']} "
                        "--status completed "
                        f"--record-dir {args.pilot_record_dir} "
                        f"--usage-record-dir {args.record_dir} "
                        f"--report {args.pilot_board_report} "
                        "--notes \"reporter completed task and shared public-safe evidence\""
                    ),
                    "purpose": "record reporter completion before converting the evidence into a usage record",
                }
            )
        commands.extend(build_conversion_commands(active_pilot, args))
    elif pilots:
        pilot = pilots[0]
        commands.extend(
            [
                {
                    "name": "prepare next pilot",
                    "command": build_prepare_next_command(pilot, args),
                    "purpose": "generate the next recommended harness, pilot pack, issue draft, and prepared-pilot record",
                },
                {
                    "name": "review pilot board",
                    "command": (
                        "codex-harness pilot-board "
                        f"--record-dir {args.pilot_record_dir} "
                        f"--usage-record-dir {args.record_dir} "
                        f"--report {args.pilot_board_report}"
                    ),
                    "purpose": "verify the prepared pilot is tracked but not counted as usage proof",
                },
                {
                    "name": "export pilot handoff",
                    "command": build_pilot_handoff_command(args),
                    "purpose": "write shareable per-pilot folders with reporter materials and maintainer commands",
                },
                {
                    "name": "audit pilot handoff",
                    "command": build_pilot_handoff_audit_command(args),
                    "purpose": "verify each handoff folder has reporter materials and an importer-shaped usage draft",
                },
                {
                    "name": "export pilot GitHub issue queue",
                    "command": build_pilot_github_issues_command(args),
                    "purpose": "write public GitHub issue bodies and gh issue create commands for active pilots",
                },
                {
                    "name": "sync pilot GitHub issue readiness",
                    "command": build_pilot_github_sync_command(args),
                    "purpose": "fetch live pilot issues and identify which reporter updates are ready to convert",
                },
            ]
        )
        commands.extend(build_conversion_commands(pilot, args))
    commands.extend(
        [
            {
                "name": "audit beta exit",
                "command": (
                    "codex-harness beta-exit-audit "
                    f"--record-dir {args.record_dir} "
                    f"--pilot-record-dir {args.pilot_record_dir} "
                    f"--usage-record-dir {args.record_dir}"
                ),
                "purpose": "refresh the non-gating readiness audit after each converted usage record",
            },
            {
                "name": "run final proof status",
                "command": f"codex-harness proof-status --beta-exit --record-dir {args.record_dir}",
                "purpose": "only use this as a beta-exit gate after usage thresholds are satisfied",
            },
        ]
    )
    return commands


def build_payload(args: argparse.Namespace) -> dict:
    gaps_payload = build_usage_gap_payload(
        Path(args.record_dir),
        min_records=args.min_records,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    board_payload = pilot_board.build_payload(Path(args.pilot_record_dir), usage_record_dir=Path(args.record_dir))
    next_pilot = (gaps_payload.get("suggested_pilots") or [None])[0]
    active_pilot = active_pilot_for_next(gaps_payload, board_payload)
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if gaps_payload["status"] == "pass" and board_payload["status"] == "pass" else "fail",
        "readiness": gaps_payload["readiness"],
        "summary": gaps_payload["summary"],
        "gaps": gaps_payload["gaps"],
        "coverage_projection": gaps_payload["coverage_projection"],
        "recommendations": gaps_payload["recommendations"],
        "next_pilot": next_pilot,
        "active_pilot": active_pilot,
        "pilot_board": {
            "status": board_payload["status"],
            "readiness": board_payload["readiness"],
            "summary": board_payload["summary"],
            "errors": board_payload["errors"],
        },
        "command_sequence": build_command_sequence(gaps_payload, active_pilot, args),
        "claim_boundary": (
            "This packet gives next actions for collecting evidence; it does not itself prove external adoption, "
            "beta-exit readiness, or production suitability."
        ),
        "does_not_prove": [
            "A prepared pilot was completed.",
            "External or multi-project usage evidence exists.",
            "The README can drop the beta label.",
            "Future generated harnesses will work well for every project.",
        ],
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Proof Next Actions",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        "This packet turns the current proof gap into the next concrete operator actions.",
        "It is a collection plan, not evidence by itself.",
        "",
        "## Current Gap",
        "",
        f"- Usage records to add: {payload['gaps']['records']}",
        f"- External or multi-project records to add: {payload['gaps']['external_or_multi_project']}",
        f"- Distinct domains to add: {payload['gaps']['domains']}",
        f"- Installed brief-based generation records to add: {payload['gaps']['installed_init_brief']}",
        "",
        "## Suggested Pilot Coverage Projection",
        "",
        payload["coverage_projection"]["claim_boundary"],
        "",
        f"- Suggested pilots in projection: {payload['coverage_projection']['candidate_pilot_count']}",
        f"- Would satisfy beta-exit usage thresholds: {str(payload['coverage_projection']['would_satisfy_beta_exit_usage_thresholds']).lower()}",
        f"- Projected usage records: {payload['coverage_projection']['projected_summary']['total']}",
        f"- Projected external or multi-project records: {payload['coverage_projection']['projected_summary']['external_or_multi_project']}",
        f"- Projected distinct domains: {payload['coverage_projection']['projected_summary']['distinct_domains']}",
        f"- Projected installed brief-based generation records: {payload['coverage_projection']['projected_summary']['installed_brief_generation']}",
        "",
        "Projected remaining gaps after suggested pilots:",
        "",
        f"- Usage records: {payload['coverage_projection']['remaining_gaps_after_candidates']['records']}",
        f"- External or multi-project records: {payload['coverage_projection']['remaining_gaps_after_candidates']['external_or_multi_project']}",
        f"- Distinct domains: {payload['coverage_projection']['remaining_gaps_after_candidates']['domains']}",
        f"- Installed brief-based generation records: {payload['coverage_projection']['remaining_gaps_after_candidates']['installed_init_brief']}",
        "",
        "## Next Pilot",
        "",
    ]
    if payload["next_pilot"]:
        pilot = payload["next_pilot"]
        lines.extend(
            [
                f"- Domain: {pilot['domain']}",
                f"- Profile: `{pilot['profile']}`",
                f"- Source type: `{pilot['source_type']}`",
                f"- Generation path: `{pilot['generation_path']}`",
                f"- Slug: `{pilot['slug']}`",
            ]
        )
    else:
        lines.append("- No pilot needed from usage gaps; run the final proof commands below.")
    lines.extend(["", "## Active Pilot", ""])
    if payload["active_pilot"]:
        active = payload["active_pilot"]
        lines.extend(
            [
                f"- Slug: `{active['slug']}`",
                f"- Status: `{active['status']}`",
                f"- Pilot pack: `{active['pilot_pack']}`",
                f"- Issue draft: `{active.get('issue_draft', '') or 'not recorded'}`",
                "",
                "Continue this pilot instead of preparing a duplicate.",
            ]
        )
    else:
        lines.append("- none")
    lines.extend(["", "## Command Sequence", ""])
    for index, item in enumerate(payload["command_sequence"], start=1):
        lines.extend(
            [
                f"{index}. {item['name']}",
                "",
                f"Purpose: {item['purpose']}",
                "",
                "```bash",
                item["command"],
                "```",
                "",
            ]
        )
    lines.extend(["## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    lines.extend(["", "## Claim Boundary", "", payload["claim_boundary"], "", "This does not prove:"])
    lines.extend(f"- {item}" for item in payload["does_not_prove"])
    text = "\n".join(lines).rstrip() + "\n"
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit("Refusing to write proof-next report with sensitive text: " + ", ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="Optional next pilot target directory")
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR_TEXT, help="Usage record JSON directory")
    parser.add_argument("--pilot-record-dir", default=DEFAULT_PILOT_RECORD_DIR_TEXT, help="Prepared-pilot tracking directory")
    parser.add_argument("--pilot-board-report", default=DEFAULT_PILOT_BOARD_REPORT_TEXT, help="Pilot board Markdown path")
    parser.add_argument("--usage-report", default=DEFAULT_USAGE_REPORT_TEXT, help="Usage records Markdown path")
    parser.add_argument("--pilot-handoff-out", default=DEFAULT_PILOT_HANDOFF_OUT_TEXT, help="Pilot handoff output directory")
    parser.add_argument("--pilot-github-issues-out", default=DEFAULT_PILOT_GITHUB_ISSUES_OUT_TEXT, help="Pilot GitHub issue body output directory")
    parser.add_argument("--pilot-github-issues-report", default=DEFAULT_PILOT_GITHUB_ISSUES_REPORT_TEXT, help="Pilot GitHub issue queue report path")
    parser.add_argument("--pilot-github-sync-report", default=DEFAULT_PILOT_GITHUB_SYNC_REPORT_TEXT, help="Pilot GitHub issue sync report path")
    parser.add_argument("--pilot-pack-out", default="/tmp/NEXT_EXTERNAL_PILOT_PACK.md", help="Pilot pack output path for the next prepare command")
    parser.add_argument("--issue-out", default="/tmp/NEXT_EXTERNAL_USAGE_ISSUE_DRAFT.md", help="Issue draft output path for the next prepare command")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="Proof-next Markdown path")
    parser.add_argument("--min-records", type=int, default=DEFAULT_TARGETS["min_records"])
    parser.add_argument("--min-external-or-multi-project", type=int, default=DEFAULT_TARGETS["min_external_or_multi_project"])
    parser.add_argument("--min-domains", type=int, default=DEFAULT_TARGETS["min_domains"])
    parser.add_argument("--min-installed-init-brief", type=int, default=DEFAULT_TARGETS["min_installed_init_brief"])
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Proof next: {payload['readiness']}")
        if payload["next_pilot"]:
            print(f"- next pilot: {payload['next_pilot']['domain']} ({payload['next_pilot']['profile']})")
        for item in payload["command_sequence"]:
            print(f"- {item['name']}: {item['command']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

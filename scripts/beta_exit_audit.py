#!/usr/bin/env python3
"""Write a non-gating audit of beta-exit readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pilot_board
import usage_gaps
from validate_usage_records import DEFAULT_RECORD_DIR


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "BETA_EXIT_AUDIT.md"
SOURCE_FRESHNESS_REPORT = REPO_ROOT / "Docs" / "Environment" / "SOURCE_FRESHNESS.md"
SEMANTIC_ALIGNMENT_REPORT = REPO_ROOT / "Docs" / "Environment" / "SEMANTIC_ALIGNMENT.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def report_status(path: Path) -> dict:
    display = path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path.as_posix()
    if not path.exists():
        return {"path": display, "status": "missing"}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return {"path": display, "status": line.split(":", 1)[1].strip().lower()}
    return {"path": display, "status": "unknown"}


def criterion(name: str, passed: bool, detail: str, command: str = "") -> dict:
    return {
        "name": name,
        "status": "pass" if passed else "missing",
        "detail": detail,
        "command": command,
    }


def build_payload(
    record_dir: Path,
    pilot_record_dir: Path,
    usage_record_dir: Path,
    min_records: int = usage_gaps.DEFAULT_TARGETS["min_records"],
    min_external_or_multi_project: int = usage_gaps.DEFAULT_TARGETS["min_external_or_multi_project"],
    min_domains: int = usage_gaps.DEFAULT_TARGETS["min_domains"],
    min_installed_init_brief: int = usage_gaps.DEFAULT_TARGETS["min_installed_init_brief"],
) -> dict:
    gaps_payload = usage_gaps.build_payload(
        record_dir,
        min_records=min_records,
        min_external_or_multi_project=min_external_or_multi_project,
        min_domains=min_domains,
        min_installed_init_brief=min_installed_init_brief,
    )
    board_payload = pilot_board.build_payload(pilot_record_dir, usage_record_dir=usage_record_dir)
    source_freshness = report_status(SOURCE_FRESHNESS_REPORT)
    semantic_alignment = report_status(SEMANTIC_ALIGNMENT_REPORT)
    summary = gaps_payload["summary"]
    gaps = gaps_payload["gaps"]
    criteria = [
        criterion(
            "non_synthetic_usage_records",
            gaps["records"] == 0,
            f"{summary['total']}/{min_records} valid usage records",
            "codex-harness usage-gaps",
        ),
        criterion(
            "external_or_multi_project_records",
            gaps["external_or_multi_project"] == 0,
            f"{summary['external_or_multi_project']}/{min_external_or_multi_project} external or multi-project records",
            "codex-harness usage-gaps",
        ),
        criterion(
            "distinct_domains",
            gaps["domains"] == 0,
            f"{summary['distinct_domains']}/{min_domains} distinct domains",
            "codex-harness usage-gaps",
        ),
        criterion(
            "installed_brief_generation",
            gaps["installed_init_brief"] == 0,
            f"{summary['installed_brief_generation']}/{min_installed_init_brief} installed brief-based generation records",
            "codex-harness usage-gaps",
        ),
        criterion(
            "source_freshness",
            source_freshness["status"] == "pass",
            f"{source_freshness['path']} status={source_freshness['status']}",
            "codex-harness source-freshness",
        ),
        criterion(
            "semantic_alignment",
            semantic_alignment["status"] == "pass",
            f"{semantic_alignment['path']} status={semantic_alignment['status']}",
            "codex-harness semantic-alignment",
        ),
        criterion(
            "release_gate",
            False,
            "Run locally and on CI before dropping the beta label.",
            "codex-harness gate",
        ),
        criterion(
            "beta_exit_proof_status",
            False,
            "Run after usage thresholds and source checks are satisfied.",
            "codex-harness proof-status --beta-exit",
        ),
    ]
    beta_exit_ready = (
        gaps_payload["readiness"] == "beta-exit-evidence-ready"
        and source_freshness["status"] == "pass"
        and semantic_alignment["status"] == "pass"
    )
    audit_valid = gaps_payload["status"] == "pass" and board_payload["status"] == "pass"
    return {
        "generated": utc_now(),
        "status": "pass" if audit_valid else "fail",
        "readiness": "beta-exit-ready-for-final-gate" if beta_exit_ready else "missing-beta-exit-evidence",
        "beta_exit_ready": beta_exit_ready,
        "criteria": criteria,
        "usage_gaps": gaps_payload,
        "pilot_board": board_payload,
        "source_freshness": source_freshness,
        "semantic_alignment": semantic_alignment,
        "next_actions": gaps_payload["recommendations"],
        "claim_boundary": "This audit reports beta-exit readiness; it does not itself prove external adoption or replace proof-status --beta-exit.",
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Beta Exit Audit",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Criteria",
        "",
        "| Criterion | Status | Detail | Command |",
        "|---|---|---|---|",
    ]
    for item in payload["criteria"]:
        command = f"`{item['command']}`" if item["command"] else ""
        lines.append(f"| `{item['name']}` | {item['status'].upper()} | {item['detail']} | {command} |")
    usage = payload["usage_gaps"]["summary"]
    gaps = payload["usage_gaps"]["gaps"]
    pilot_summary = payload["pilot_board"]["summary"]
    lines.extend(
        [
            "",
            "## Current Evidence",
            "",
            f"- Usage records: {usage['total']}",
            f"- External or multi-project records: {usage['external_or_multi_project']}",
            f"- Distinct domains: {usage['distinct_domains']}",
            f"- Installed brief-based generation records: {usage['installed_brief_generation']}",
            f"- Pending pilots: {pilot_summary['pending']}",
            f"- Completed but not converted pilots: {pilot_summary['completed_not_converted']}",
            f"- Converted pilots with validated usage records: {pilot_summary['converted_validated']}",
            "",
            "## Remaining Usage Gaps",
            "",
            f"- Usage records: {gaps['records']}",
            f"- External or multi-project records: {gaps['external_or_multi_project']}",
            f"- Distinct domains: {gaps['domains']}",
            f"- Installed brief-based generation records: {gaps['installed_init_brief']}",
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["next_actions"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--pilot-record-dir", default=pilot_board.DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--usage-record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(
        Path(args.record_dir),
        pilot_record_dir=Path(args.pilot_record_dir),
        usage_record_dir=Path(args.usage_record_dir),
    )
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Beta exit audit: {payload['readiness']}")
        for item in payload["criteria"]:
            print(f"- {item['name']}: {item['status'].upper()} - {item['detail']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Summarize product-proof readiness from checked-in evidence artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_usage_records import DEFAULT_RECORD_DIR, validate_record_dir
from check_example_inventory import check_inventory
from check_cli_install import build_payload as build_cli_install_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
PROOF_MATRIX = REPO_ROOT / "Docs" / "Environment" / "PROOF_MATRIX.md"
USAGE_REPORT = REPO_ROOT / "Docs" / "Environment" / "USAGE_RECORDS.md"
USAGE_GAPS_REPORT = REPO_ROOT / "Docs" / "Environment" / "USAGE_GAPS.md"
PILOT_CAMPAIGN_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_CAMPAIGN.md"
TASK_TRIALS_REPORT = REPO_ROOT / "examples" / "live-create" / "TASK_TRIALS.md"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PROOF_STATUS.md"
TASK_TRIAL_ROW_RE = re.compile(r"^\| `(?P<trial>[^`]+)` \| `(?P<example>[^`]+)` \| (?P<status>[A-Z]+) \| `(?P<output>[^`]+)` \|$")


def parse_status_line(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def parse_task_trials(path: Path) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "status": "missing",
            "trial_count": 0,
            "pass_count": 0,
            "failed_trials": [],
        }
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        match = TASK_TRIAL_ROW_RE.match(line)
        if match:
            rows.append(match.groupdict())
    failed = [row["trial"] for row in rows if row["status"].lower() != "pass"]
    return {
        "exists": True,
        "status": parse_status_line(text) or "unknown",
        "trial_count": len(rows),
        "pass_count": sum(1 for row in rows if row["status"].lower() == "pass"),
        "failed_trials": failed,
    }


def check_file_exists(name: str, path: Path) -> dict:
    return {
        "name": name,
        "status": "pass" if path.exists() else "fail",
        "detail": path.relative_to(REPO_ROOT).as_posix() if path.exists() else f"missing: {path.relative_to(REPO_ROOT).as_posix()}",
    }


def check_installable_cli() -> tuple[dict, dict]:
    payload = build_cli_install_payload()
    failed = next((step for step in payload["steps"] if step["status"] != "pass"), None)
    profile_step = next((step for step in payload["steps"] if step["name"] == "profiles"), {})
    doctor_step = next((step for step in payload["steps"] if step["name"] == "doctor"), {})
    init_step = next((step for step in payload["steps"] if step["name"] == "init"), {})
    init_from_project_step = next((step for step in payload["steps"] if step["name"] == "init_from_project"), {})
    demo_step = next((step for step in payload["steps"] if step["name"] == "demo_capture"), {})
    validate_step = next((step for step in payload["steps"] if step["name"] == "validate"), {})
    inspect_step = next((step for step in payload["steps"] if step["name"] == "inspect"), {})
    adoption_step = next((step for step in payload["steps"] if step["name"] == "adoption_plan"), {})
    local_eval_step = next((step for step in payload["steps"] if step["name"] == "local_eval"), {})
    evidence_packet_step = next((step for step in payload["steps"] if step["name"] == "evidence_packet"), {})
    pilot_pack_step = next((step for step in payload["steps"] if step["name"] == "pilot_pack"), {})
    usage_from_harness_step = next((step for step in payload["steps"] if step["name"] == "usage_from_harness"), {})
    usage_from_issue_step = next((step for step in payload["steps"] if step["name"] == "usage_from_issue"), {})
    usage_gaps_step = next((step for step in payload["steps"] if step["name"] == "usage_gaps"), {})
    pilot_campaign_step = next((step for step in payload["steps"] if step["name"] == "pilot_campaign"), {})
    migration_step = next((step for step in payload["steps"] if step["name"] == "migration_audit"), {})
    eval_step = next((step for step in payload["steps"] if step["name"] == "eval"), {})
    if failed:
        detail = f"failed at {failed['name']}"
    else:
        detail = "profiles={profiles} doctor={doctor_status} init={init_status} init_from_project={init_from_project_status} demo_capture={demo_status} validate={validate_status} inspect={inspect_status} adoption_plan={adoption_status} local_eval={local_eval_status} evidence_packet={evidence_packet_status} pilot_pack={pilot_pack_status} usage_from_harness={usage_from_harness_status} usage_from_issue={usage_from_issue_status} usage_gaps={usage_gaps_status} pilot_campaign={pilot_campaign_status} migration_audit={migration_status} eval={eval_status}".format(
            profiles=profile_step.get("profile_count", "unknown"),
            doctor_status=doctor_step.get("status", "unknown"),
            init_status=init_step.get("status", "unknown"),
            init_from_project_status=init_from_project_step.get("status", "unknown"),
            demo_status=demo_step.get("status", "unknown"),
            validate_status=validate_step.get("status", "unknown"),
            inspect_status=inspect_step.get("status", "unknown"),
            adoption_status=adoption_step.get("status", "unknown"),
            local_eval_status=local_eval_step.get("status", "unknown"),
            evidence_packet_status=evidence_packet_step.get("status", "unknown"),
            pilot_pack_status=pilot_pack_step.get("status", "unknown"),
            usage_from_harness_status=usage_from_harness_step.get("status", "unknown"),
            usage_from_issue_status=usage_from_issue_step.get("status", "unknown"),
            usage_gaps_status=usage_gaps_step.get("status", "unknown"),
            pilot_campaign_status=pilot_campaign_step.get("status", "unknown"),
            migration_status=migration_step.get("status", "unknown"),
            eval_status=eval_step.get("status", "unknown"),
        )
    return (
        {
            "name": "installable_cli",
            "status": payload["status"],
            "detail": detail,
        },
        payload,
    )


def build_payload(
    min_live_trials: int,
    min_usage_records: int,
    record_dir: Path,
    min_external_or_multi_project: int = 0,
    min_domains: int = 0,
    min_installed_init_brief: int = 0,
) -> dict:
    task_trials = parse_task_trials(TASK_TRIALS_REPORT)
    inventory = check_inventory()
    install_check, install_payload = check_installable_cli()
    usage = validate_record_dir(
        record_dir,
        min_records=min_usage_records,
        require_non_synthetic=True,
        require_success=True,
        min_external_or_multi_project=min_external_or_multi_project,
        min_domains=min_domains,
        min_installed_init_brief=min_installed_init_brief,
    )
    checks = [
        check_file_exists("proof_matrix", PROOF_MATRIX),
        check_file_exists("usage_report", USAGE_REPORT),
        check_file_exists("usage_gaps_report", USAGE_GAPS_REPORT),
        check_file_exists("pilot_campaign_report", PILOT_CAMPAIGN_REPORT),
        check_file_exists("task_trials_report", TASK_TRIALS_REPORT),
        {
            "name": "checked_in_example_inventory",
            "status": inventory["status"],
            "detail": "profiles={profile_count} brief_examples={brief_example_count} failures={failure_count}".format(**inventory),
        },
        install_check,
        {
            "name": "live_task_trials",
            "status": (
                "pass"
                if task_trials["exists"]
                and task_trials["status"] == "pass"
                and task_trials["trial_count"] >= min_live_trials
                and not task_trials["failed_trials"]
                else "fail"
            ),
            "detail": f"{task_trials['pass_count']}/{task_trials['trial_count']} pass; required >= {min_live_trials}",
        },
        {
            "name": "non_synthetic_usage",
            "status": usage["status"],
            "detail": "records={total} non_synthetic={non_synthetic} success={success} external_or_multi_project={external_or_multi_project} domains={distinct_domains} installed_init_brief={installed_init_brief}".format(
                **usage["summary"]
            ),
            "requirement_errors": usage["requirement_errors"],
        },
    ]
    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "readiness": (
            "Codex-equivalent beta with checked-in self-dogfood proof"
            if status == "pass"
            else "Incomplete proof package"
        ),
        "checks": checks,
        "example_inventory": inventory,
        "installable_cli": install_payload,
        "task_trials": task_trials,
        "usage_summary": usage["summary"],
        "does_not_prove": [
            "Broad external adoption.",
            "Longitudinal performance across many private repos.",
            "Every future live model-mediated /create run will be ideal.",
            "Organization-level compliance, policy enforcement, or production security controls.",
        ],
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Proof Status",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        "This report summarizes checked-in evidence. It is intentionally",
        "conservative and should be read with `PROOF_MATRIX.md`.",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in payload["checks"]:
        lines.append(f"| `{check['name']}` | {check['status'].upper()} | {check['detail']} |")
    usage = payload["usage_summary"]
    lines.extend(
        [
            "",
            "## Usage Evidence",
            "",
            f"- Total records: {usage['total']}",
            f"- Non-synthetic records: {usage['non_synthetic']}",
            f"- Successful records: {usage['success']}",
            f"- External or multi-project records: {usage['external_or_multi_project']}",
            f"- Distinct domains: {usage['distinct_domains']}",
            f"- Installed init --brief records: {usage['installed_init_brief']}",
            "",
            "## What This Does Not Prove",
            "",
        ]
    )
    for item in payload["does_not_prove"]:
        lines.append(f"- {item}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-live-trials", type=int, default=8, help="Minimum passing live task trials required")
    parser.add_argument("--min-usage-records", type=int, default=2, help="Minimum valid usage records required")
    parser.add_argument("--min-external-or-multi-project", type=int, default=0, help="Minimum external or multi-project usage records")
    parser.add_argument("--min-domains", type=int, default=0, help="Minimum distinct usage domains")
    parser.add_argument("--min-installed-init-brief", type=int, default=0, help="Minimum usage records generated via installed init --brief")
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write PROOF_STATUS.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    payload = build_payload(
        min_live_trials=args.min_live_trials,
        min_usage_records=args.min_usage_records,
        record_dir=Path(args.record_dir),
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Proof status: {payload['status'].upper()}")
        print(f"- readiness: {payload['readiness']}")
        for check in payload["checks"]:
            print(f"- {check['name']}: {check['status'].upper()} - {check['detail']}")
            for error in check.get("requirement_errors", []):
                print(f"  requirement: {error}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

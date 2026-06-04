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
EQUIVALENCE_MATRIX = REPO_ROOT / "Docs" / "Environment" / "CODEX_EQUIVALENCE_MATRIX.md"
USAGE_REPORT = REPO_ROOT / "Docs" / "Environment" / "USAGE_RECORDS.md"
USAGE_GAPS_REPORT = REPO_ROOT / "Docs" / "Environment" / "USAGE_GAPS.md"
PILOT_CAMPAIGN_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_CAMPAIGN.md"
PILOT_BOARD_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_BOARD.md"
PROOF_NEXT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PROOF_NEXT.md"
BETA_EXIT_AUDIT_REPORT = REPO_ROOT / "Docs" / "Environment" / "BETA_EXIT_AUDIT.md"
UPSTREAM_DRIFT_REPORT = REPO_ROOT / "Docs" / "Environment" / "UPSTREAM_DRIFT.md"
SOURCE_FRESHNESS_REPORT = REPO_ROOT / "Docs" / "Environment" / "SOURCE_FRESHNESS.md"
SOURCE_FRESHNESS_JSON = REPO_ROOT / "Docs" / "Environment" / "SOURCE_FRESHNESS.json"
SEMANTIC_ALIGNMENT_REPORT = REPO_ROOT / "Docs" / "Environment" / "SEMANTIC_ALIGNMENT.md"
SEMANTIC_ALIGNMENT_JSON = REPO_ROOT / "Docs" / "Environment" / "SEMANTIC_ALIGNMENT.json"
TASK_TRIALS_REPORT = REPO_ROOT / "examples" / "live-create" / "TASK_TRIALS.md"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PROOF_STATUS.md"
TASK_TRIAL_ROW_RE = re.compile(r"^\| `(?P<trial>[^`]+)` \| `(?P<example>[^`]+)` \| (?P<status>[A-Z]+) \| `(?P<output>[^`]+)` \|$")
DEFAULT_MIN_LIVE_TRIALS = 8
DEFAULT_MIN_USAGE_RECORDS = 2
BETA_EXIT_MIN_USAGE_RECORDS = 5
BETA_EXIT_MIN_EXTERNAL_OR_MULTI_PROJECT = 3
BETA_EXIT_MIN_DOMAINS = 4
BETA_EXIT_MIN_INSTALLED_INIT_BRIEF = 2


def parse_status_line(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip().lower()
    return None


def parse_generated_line(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("Generated:"):
            return line.split(":", 1)[1].strip()
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


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check_file_exists(name: str, path: Path) -> dict:
    return {
        "name": name,
        "status": "pass" if path.exists() else "fail",
        "detail": display_path(path) if path.exists() else f"missing: {display_path(path)}",
    }


def check_status_report(name: str, report_path: Path, json_path: Path) -> dict:
    missing = [path for path in (report_path, json_path) if not path.exists()]
    if missing:
        missing_detail = ", ".join(display_path(path) for path in missing)
        return {
            "name": name,
            "status": "fail",
            "detail": f"missing: {missing_detail}",
        }

    report_text = report_path.read_text(encoding="utf-8")
    report_status = parse_status_line(report_text) or "unknown"
    generated = parse_generated_line(report_text) or "unknown"
    try:
        json_payload = json.loads(json_path.read_text(encoding="utf-8"))
        json_status = str(json_payload.get("status", "unknown")).lower()
    except json.JSONDecodeError as exc:
        json_status = "invalid-json"
        generated = generated if generated != "unknown" else f"json error: {exc}"

    status = "pass" if report_status == "pass" and json_status == "pass" else "fail"
    return {
        "name": name,
        "status": status,
        "detail": (
            f"report={display_path(report_path)} "
            f"status={report_status} json_status={json_status} generated={generated}"
        ),
    }


def check_installable_cli() -> tuple[dict, dict]:
    payload = build_cli_install_payload()
    failed = next((step for step in payload["steps"] if step["status"] != "pass"), None)
    profile_step = next((step for step in payload["steps"] if step["name"] == "profiles"), {})
    doctor_step = next((step for step in payload["steps"] if step["name"] == "doctor"), {})
    init_step = next((step for step in payload["steps"] if step["name"] == "init"), {})
    quickstart_step = next((step for step in payload["steps"] if step["name"] == "quickstart"), {})
    prepare_pilot_step = next((step for step in payload["steps"] if step["name"] == "prepare_pilot"), {})
    init_from_project_step = next((step for step in payload["steps"] if step["name"] == "init_from_project"), {})
    demo_step = next((step for step in payload["steps"] if step["name"] == "demo_capture"), {})
    validate_step = next((step for step in payload["steps"] if step["name"] == "validate"), {})
    inspect_step = next((step for step in payload["steps"] if step["name"] == "inspect"), {})
    adoption_step = next((step for step in payload["steps"] if step["name"] == "adoption_plan"), {})
    equivalence_step = next((step for step in payload["steps"] if step["name"] == "equivalence"), {})
    upstream_drift_step = next((step for step in payload["steps"] if step["name"] == "upstream_drift"), {})
    local_eval_step = next((step for step in payload["steps"] if step["name"] == "local_eval"), {})
    public_usage_report_step = next((step for step in payload["steps"] if step["name"] == "public_usage_report"), {})
    evidence_packet_step = next((step for step in payload["steps"] if step["name"] == "evidence_packet"), {})
    pilot_pack_step = next((step for step in payload["steps"] if step["name"] == "pilot_pack"), {})
    usage_from_harness_step = next((step for step in payload["steps"] if step["name"] == "usage_from_harness"), {})
    usage_from_issue_lint_step = next((step for step in payload["steps"] if step["name"] == "usage_from_issue_lint"), {})
    usage_from_issue_preview_step = next((step for step in payload["steps"] if step["name"] == "usage_from_issue_preview"), {})
    usage_from_issue_step = next((step for step in payload["steps"] if step["name"] == "usage_from_issue"), {})
    prepare_next_pilot_step = next((step for step in payload["steps"] if step["name"] == "prepare_next_pilot"), {})
    prepare_pilot_batch_step = next(
        (step for step in payload["steps"] if step["name"] == "prepare_pilot_batch_dry_run"), {}
    )
    pilot_board_step = next((step for step in payload["steps"] if step["name"] == "pilot_board"), {})
    pilot_update_step = next((step for step in payload["steps"] if step["name"] == "pilot_update"), {})
    usage_from_issue_pilot_conversion_step = next(
        (step for step in payload["steps"] if step["name"] == "usage_from_issue_pilot_conversion"), {}
    )
    usage_gaps_step = next((step for step in payload["steps"] if step["name"] == "usage_gaps"), {})
    beta_exit_audit_step = next((step for step in payload["steps"] if step["name"] == "beta_exit_audit"), {})
    pilot_campaign_step = next((step for step in payload["steps"] if step["name"] == "pilot_campaign"), {})
    proof_next_step = next((step for step in payload["steps"] if step["name"] == "proof_next"), {})
    migration_step = next((step for step in payload["steps"] if step["name"] == "migration_audit"), {})
    eval_step = next((step for step in payload["steps"] if step["name"] == "eval"), {})
    if failed:
        detail = f"failed at {failed['name']}"
    else:
        detail = "profiles={profiles} doctor={doctor_status} init={init_status} quickstart={quickstart_status} prepare_pilot={prepare_pilot_status} init_from_project={init_from_project_status} demo_capture={demo_status} validate={validate_status} inspect={inspect_status} adoption_plan={adoption_status} equivalence={equivalence_status} upstream_drift={upstream_drift_status} local_eval={local_eval_status} public_usage_report={public_usage_report_status} evidence_packet={evidence_packet_status} pilot_pack={pilot_pack_status} usage_from_harness={usage_from_harness_status} usage_from_issue_lint={usage_from_issue_lint_status} usage_from_issue_preview={usage_from_issue_preview_status} usage_from_issue={usage_from_issue_status} prepare_next_pilot={prepare_next_pilot_status} prepare_pilot_batch={prepare_pilot_batch_status} pilot_board={pilot_board_status} pilot_update={pilot_update_status} usage_from_issue_pilot_conversion={usage_from_issue_pilot_conversion_status} usage_gaps={usage_gaps_status} beta_exit_audit={beta_exit_audit_status} pilot_campaign={pilot_campaign_status} proof_next={proof_next_status} migration_audit={migration_status} eval={eval_status}".format(
            profiles=profile_step.get("profile_count", "unknown"),
            doctor_status=doctor_step.get("status", "unknown"),
            init_status=init_step.get("status", "unknown"),
            quickstart_status=quickstart_step.get("status", "unknown"),
            prepare_pilot_status=prepare_pilot_step.get("status", "unknown"),
            init_from_project_status=init_from_project_step.get("status", "unknown"),
            demo_status=demo_step.get("status", "unknown"),
            validate_status=validate_step.get("status", "unknown"),
            inspect_status=inspect_step.get("status", "unknown"),
            adoption_status=adoption_step.get("status", "unknown"),
            equivalence_status=equivalence_step.get("status", "unknown"),
            upstream_drift_status=upstream_drift_step.get("status", "unknown"),
            local_eval_status=local_eval_step.get("status", "unknown"),
            public_usage_report_status=public_usage_report_step.get("status", "unknown"),
            evidence_packet_status=evidence_packet_step.get("status", "unknown"),
            pilot_pack_status=pilot_pack_step.get("status", "unknown"),
            usage_from_harness_status=usage_from_harness_step.get("status", "unknown"),
            usage_from_issue_lint_status=usage_from_issue_lint_step.get("status", "unknown"),
            usage_from_issue_preview_status=usage_from_issue_preview_step.get("status", "unknown"),
            usage_from_issue_status=usage_from_issue_step.get("status", "unknown"),
            prepare_next_pilot_status=prepare_next_pilot_step.get("status", "unknown"),
            prepare_pilot_batch_status=prepare_pilot_batch_step.get("status", "unknown"),
            pilot_board_status=pilot_board_step.get("status", "unknown"),
            pilot_update_status=pilot_update_step.get("status", "unknown"),
            usage_from_issue_pilot_conversion_status=usage_from_issue_pilot_conversion_step.get("status", "unknown"),
            usage_gaps_status=usage_gaps_step.get("status", "unknown"),
            beta_exit_audit_status=beta_exit_audit_step.get("status", "unknown"),
            pilot_campaign_status=pilot_campaign_step.get("status", "unknown"),
            proof_next_status=proof_next_step.get("status", "unknown"),
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
    proof_mode: str = "self-dogfood-proof",
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
        check_file_exists("equivalence_matrix", EQUIVALENCE_MATRIX),
        check_file_exists("usage_report", USAGE_REPORT),
        check_file_exists("usage_gaps_report", USAGE_GAPS_REPORT),
        check_file_exists("pilot_campaign_report", PILOT_CAMPAIGN_REPORT),
        check_file_exists("pilot_board_report", PILOT_BOARD_REPORT),
        check_file_exists("proof_next_report", PROOF_NEXT_REPORT),
        check_file_exists("beta_exit_audit_report", BETA_EXIT_AUDIT_REPORT),
        check_file_exists("upstream_drift_report", UPSTREAM_DRIFT_REPORT),
        check_status_report("source_freshness_report", SOURCE_FRESHNESS_REPORT, SOURCE_FRESHNESS_JSON),
        check_status_report("semantic_alignment_report", SEMANTIC_ALIGNMENT_REPORT, SEMANTIC_ALIGNMENT_JSON),
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
            "detail": "records={total} non_synthetic={non_synthetic} success={success} external_or_multi_project={external_or_multi_project} domains={distinct_domains} installed_brief_generation={installed_brief_generation}".format(
                **usage["summary"]
            ),
            "requirement_errors": usage["requirement_errors"],
        },
    ]
    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    if proof_mode == "beta-exit":
        readiness = "Beta exit proof complete" if status == "pass" else "Missing beta-exit evidence"
    else:
        readiness = (
            "Codex-equivalent beta with checked-in self-dogfood proof"
            if status == "pass"
            else "Incomplete proof package"
        )
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "mode": proof_mode,
        "readiness": readiness,
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
        f"Mode: {payload['mode']}",
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
    requirement_errors = [
        (check["name"], error)
        for check in payload["checks"]
        for error in check.get("requirement_errors", [])
    ]
    if requirement_errors:
        lines.extend(["", "## Requirements Not Met", ""])
        for check_name, error in requirement_errors:
            lines.append(f"- `{check_name}`: {error}")
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
            f"- Installed brief-based generation records: {usage['installed_brief_generation']}",
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
    parser.add_argument("--beta-exit", action="store_true", help="Apply roadmap beta-exit thresholds")
    parser.add_argument("--min-live-trials", type=int, help="Minimum passing live task trials required")
    parser.add_argument("--min-usage-records", type=int, help="Minimum valid usage records required")
    parser.add_argument("--min-external-or-multi-project", type=int, help="Minimum external or multi-project usage records")
    parser.add_argument("--min-domains", type=int, help="Minimum distinct usage domains")
    parser.add_argument("--min-installed-init-brief", type=int, help="Minimum usage records generated via installed brief-based generation")
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write PROOF_STATUS.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    proof_mode = "beta-exit" if args.beta_exit else "self-dogfood-proof"
    min_live_trials = args.min_live_trials if args.min_live_trials is not None else DEFAULT_MIN_LIVE_TRIALS
    if args.beta_exit:
        min_usage_records = (
            args.min_usage_records
            if args.min_usage_records is not None
            else BETA_EXIT_MIN_USAGE_RECORDS
        )
        min_external_or_multi_project = (
            args.min_external_or_multi_project
            if args.min_external_or_multi_project is not None
            else BETA_EXIT_MIN_EXTERNAL_OR_MULTI_PROJECT
        )
        min_domains = args.min_domains if args.min_domains is not None else BETA_EXIT_MIN_DOMAINS
        min_installed_init_brief = (
            args.min_installed_init_brief
            if args.min_installed_init_brief is not None
            else BETA_EXIT_MIN_INSTALLED_INIT_BRIEF
        )
    else:
        min_usage_records = args.min_usage_records if args.min_usage_records is not None else DEFAULT_MIN_USAGE_RECORDS
        min_external_or_multi_project = (
            args.min_external_or_multi_project
            if args.min_external_or_multi_project is not None
            else 0
        )
        min_domains = args.min_domains if args.min_domains is not None else 0
        min_installed_init_brief = (
            args.min_installed_init_brief
            if args.min_installed_init_brief is not None
            else 0
        )

    payload = build_payload(
        min_live_trials=min_live_trials,
        min_usage_records=min_usage_records,
        record_dir=Path(args.record_dir),
        min_external_or_multi_project=min_external_or_multi_project,
        min_domains=min_domains,
        min_installed_init_brief=min_installed_init_brief,
        proof_mode=proof_mode,
    )
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Proof status: {payload['status'].upper()}")
        print(f"- mode: {payload['mode']}")
        print(f"- readiness: {payload['readiness']}")
        for check in payload["checks"]:
            print(f"- {check['name']}: {check['status'].upper()} - {check['detail']}")
            for error in check.get("requirement_errors", []):
                print(f"  requirement: {error}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

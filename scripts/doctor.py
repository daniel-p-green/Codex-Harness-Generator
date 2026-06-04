#!/usr/bin/env python3
"""Fast local readiness check for Codex Harness Generator contributors."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_cli_install import build_payload as build_cli_install_payload
from check_example_inventory import check_inventory
from generate_minimal_harness import PROFILES
from validate_usage_records import DEFAULT_RECORD_DIR, validate_record_dir


REPO_ROOT = Path(__file__).resolve().parents[1]
PROOF_STATUS_REPORT = REPO_ROOT / "Docs" / "Environment" / "PROOF_STATUS.md"

REQUIRED_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "pyproject.toml",
    ".github/workflows/evals.yml",
    ".github/ISSUE_TEMPLATE/bug-report.yml",
    ".github/ISSUE_TEMPLATE/external-usage-report.yml",
    ".github/ISSUE_TEMPLATE/feature-request.yml",
    "Docs/Environment/PROOF_MATRIX.md",
    "Docs/Environment/ROADMAP.md",
    "Docs/Environment/CODEX_EQUIVALENCE_MATRIX.md",
    "Docs/Environment/USAGE_GAPS.md",
    "Docs/Environment/USAGE_RECORDS.md",
    "Docs/Environment/PILOT_CAMPAIGN.md",
    "Docs/Environment/PILOT_BOARD.md",
    "scripts/codex_harness.py",
    "scripts/generate_minimal_harness.py",
    "scripts/inspect_project.py",
    "scripts/run_quickstart.py",
    "scripts/run_inspected_acceptance.py",
    "scripts/run_evals.py",
)

NEXT_COMMANDS = (
    "codex-harness profiles",
    "codex-harness inspect .",
    'codex-harness quickstart /tmp/codex-rag-harness --brief "RAG app with prompts, evals, and retrieval checks" --force',
    'codex-harness init /tmp/codex-rag-harness --brief "RAG app with prompts, evals, and retrieval checks" --force',
    "codex-harness validate /tmp/codex-rag-harness",
    "codex-harness gate",
)


def status_from_report(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip().lower()
    return "unknown"


def check_required_files(repo_root: Path = REPO_ROOT, required_files: tuple[str, ...] = REQUIRED_FILES) -> dict:
    missing = [path for path in required_files if not (repo_root / path).exists()]
    return {
        "name": "required_files",
        "status": "pass" if not missing else "fail",
        "detail": f"{len(required_files) - len(missing)}/{len(required_files)} present",
        "missing": missing,
    }


def check_python_version(minimum: tuple[int, int] = (3, 10)) -> dict:
    current = sys.version_info
    status = "pass" if (current.major, current.minor) >= minimum else "fail"
    return {
        "name": "python_version",
        "status": status,
        "detail": f"{current.major}.{current.minor}.{current.micro}; required >= {minimum[0]}.{minimum[1]}",
    }


def check_profiles(min_profile_count: int = 20) -> dict:
    profile_count = len(PROFILES)
    return {
        "name": "profile_catalog",
        "status": "pass" if profile_count >= min_profile_count else "fail",
        "detail": f"{profile_count} supported profiles; required >= {min_profile_count}",
    }


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check_proof_status_report(path: Path = PROOF_STATUS_REPORT) -> dict:
    report_status = status_from_report(path)
    if report_status is None:
        return {
            "name": "proof_status_report",
            "status": "fail",
            "detail": f"missing: {display_path(path)}",
        }
    return {
        "name": "proof_status_report",
        "status": "pass",
        "detail": f"{display_path(path)} last_status={report_status}",
    }


def check_usage_records(record_dir: Path, min_usage_records: int) -> tuple[dict, dict]:
    payload = validate_record_dir(
        record_dir,
        min_records=min_usage_records,
        require_non_synthetic=True,
        require_success=True,
    )
    summary = payload["summary"]
    return (
        {
            "name": "usage_records",
            "status": payload["status"],
            "detail": "records={total} non_synthetic={non_synthetic} success={success}; required >= {required}".format(
                required=min_usage_records,
                **summary,
            ),
            "requirement_errors": payload["requirement_errors"],
        },
        payload,
    )


def check_installable_cli() -> tuple[dict, dict]:
    payload = build_cli_install_payload()
    failed = next((step for step in payload["steps"] if step["status"] != "pass"), None)
    profile_step = next((step for step in payload["steps"] if step["name"] == "profiles"), {})
    doctor_step = next((step for step in payload["steps"] if step["name"] == "doctor"), {})
    quickstart_step = next((step for step in payload["steps"] if step["name"] == "quickstart"), {})
    prepare_pilot_step = next((step for step in payload["steps"] if step["name"] == "prepare_pilot"), {})
    init_from_project_step = next((step for step in payload["steps"] if step["name"] == "init_from_project"), {})
    validate_step = next((step for step in payload["steps"] if step["name"] == "validate"), {})
    inspect_step = next((step for step in payload["steps"] if step["name"] == "inspect"), {})
    adoption_step = next((step for step in payload["steps"] if step["name"] == "adoption_plan"), {})
    equivalence_step = next((step for step in payload["steps"] if step["name"] == "equivalence"), {})
    local_eval_step = next((step for step in payload["steps"] if step["name"] == "local_eval"), {})
    public_usage_report_step = next((step for step in payload["steps"] if step["name"] == "public_usage_report"), {})
    evidence_packet_step = next((step for step in payload["steps"] if step["name"] == "evidence_packet"), {})
    pilot_pack_step = next((step for step in payload["steps"] if step["name"] == "pilot_pack"), {})
    usage_from_harness_step = next((step for step in payload["steps"] if step["name"] == "usage_from_harness"), {})
    usage_from_issue_preview_step = next((step for step in payload["steps"] if step["name"] == "usage_from_issue_preview"), {})
    usage_from_issue_step = next((step for step in payload["steps"] if step["name"] == "usage_from_issue"), {})
    prepare_next_pilot_step = next((step for step in payload["steps"] if step["name"] == "prepare_next_pilot"), {})
    pilot_board_step = next((step for step in payload["steps"] if step["name"] == "pilot_board"), {})
    pilot_update_step = next((step for step in payload["steps"] if step["name"] == "pilot_update"), {})
    usage_gaps_step = next((step for step in payload["steps"] if step["name"] == "usage_gaps"), {})
    pilot_campaign_step = next((step for step in payload["steps"] if step["name"] == "pilot_campaign"), {})
    migration_step = next((step for step in payload["steps"] if step["name"] == "migration_audit"), {})
    if failed:
        detail = f"failed at {failed['name']}"
    else:
        detail = "profiles={profiles} doctor={doctor_status} init=pass quickstart={quickstart_status} prepare_pilot={prepare_pilot_status} init_from_project={init_from_project_status} validate={validate_status} inspect={inspect_status} adoption_plan={adoption_status} equivalence={equivalence_status} local_eval={local_eval_status} public_usage_report={public_usage_report_status} evidence_packet={evidence_packet_status} pilot_pack={pilot_pack_status} usage_from_harness={usage_from_harness_status} usage_from_issue_preview={usage_from_issue_preview_status} usage_from_issue={usage_from_issue_status} prepare_next_pilot={prepare_next_pilot_status} pilot_board={pilot_board_status} pilot_update={pilot_update_status} usage_gaps={usage_gaps_status} pilot_campaign={pilot_campaign_status} migration_audit={migration_status} eval=pass".format(
            profiles=profile_step.get("profile_count", "unknown"),
            doctor_status=doctor_step.get("status", "unknown"),
            quickstart_status=quickstart_step.get("status", "unknown"),
            prepare_pilot_status=prepare_pilot_step.get("status", "unknown"),
            init_from_project_status=init_from_project_step.get("status", "unknown"),
            validate_status=validate_step.get("status", "unknown"),
            inspect_status=inspect_step.get("status", "unknown"),
            adoption_status=adoption_step.get("status", "unknown"),
            equivalence_status=equivalence_step.get("status", "unknown"),
            local_eval_status=local_eval_step.get("status", "unknown"),
            public_usage_report_status=public_usage_report_step.get("status", "unknown"),
            evidence_packet_status=evidence_packet_step.get("status", "unknown"),
            pilot_pack_status=pilot_pack_step.get("status", "unknown"),
            usage_from_harness_status=usage_from_harness_step.get("status", "unknown"),
            usage_from_issue_preview_status=usage_from_issue_preview_step.get("status", "unknown"),
            usage_from_issue_status=usage_from_issue_step.get("status", "unknown"),
            prepare_next_pilot_status=prepare_next_pilot_step.get("status", "unknown"),
            pilot_board_status=pilot_board_step.get("status", "unknown"),
            pilot_update_status=pilot_update_step.get("status", "unknown"),
            usage_gaps_status=usage_gaps_step.get("status", "unknown"),
            pilot_campaign_status=pilot_campaign_step.get("status", "unknown"),
            migration_status=migration_step.get("status", "unknown"),
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
    record_dir: Path = DEFAULT_RECORD_DIR,
    min_usage_records: int = 2,
    include_install_smoke: bool = False,
) -> dict:
    inventory = check_inventory()
    usage_check, usage_payload = check_usage_records(record_dir, min_usage_records)
    checks = [
        check_python_version(),
        check_required_files(),
        check_profiles(),
        {
            "name": "example_inventory",
            "status": inventory["status"],
            "detail": "profiles={profile_count} brief_examples={brief_example_count} failures={failure_count}".format(**inventory),
        },
        usage_check,
        check_proof_status_report(),
    ]
    install_payload = None
    if include_install_smoke:
        install_check, install_payload = check_installable_cli()
        checks.append(install_check)

    status = "pass" if all(check["status"] == "pass" for check in checks) else "fail"
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "readiness": "local checkout is ready for generation and release-gate work" if status == "pass" else "local checkout needs attention",
        "checks": checks,
        "example_inventory": inventory,
        "usage_records": usage_payload,
        "installable_cli": install_payload,
        "next_commands": list(NEXT_COMMANDS),
        "notes": [
            "doctor is fast by default and does not replace the full release gate.",
            "Use --include-install-smoke before publishing packaging or console-script changes.",
        ],
    }


def print_text(payload: dict) -> None:
    print(f"Codex Harness Doctor: {payload['status'].upper()}")
    print(f"- readiness: {payload['readiness']}")
    for check in payload["checks"]:
        print(f"- {check['name']}: {check['status'].upper()} - {check['detail']}")
        for missing in check.get("missing", []):
            print(f"  missing: {missing}")
        for error in check.get("requirement_errors", []):
            print(f"  requirement: {error}")
    print("- next:")
    for command in payload["next_commands"]:
        print(f"  {command}")
    for note in payload["notes"]:
        print(f"- note: {note}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix(), help="Directory where usage record JSON files are read")
    parser.add_argument("--min-usage-records", type=int, default=2, help="Minimum valid usage records required")
    parser.add_argument("--include-install-smoke", action="store_true", help="Also run the slower non-editable CLI install smoke")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args(argv)

    payload = build_payload(
        record_dir=Path(args.record_dir),
        min_usage_records=args.min_usage_records,
        include_install_smoke=args.include_install_smoke,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

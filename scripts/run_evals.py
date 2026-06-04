#!/usr/bin/env python3
"""Run the full Codex Harness Generator eval gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses"
DETERMINISTIC_EXAMPLE_ROOT = REPO_ROOT / "examples" / "deterministic"
CREATE_ACCEPTANCE_EXAMPLE_ROOT = REPO_ROOT / "examples" / "create-acceptance"
LIVE_CREATE_EXAMPLE_ROOT = REPO_ROOT / "examples" / "live-create"


def run_step(name: str, command: list[str]) -> dict:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "status": "pass" if completed.returncode == 0 else "fail",
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def fixture_paths() -> list[str]:
    return [
        path.as_posix()
        for path in sorted(FIXTURE_ROOT.iterdir())
        if path.is_dir()
    ]


def deterministic_example_paths() -> list[str]:
    if not DETERMINISTIC_EXAMPLE_ROOT.exists():
        return []
    return [
        path.as_posix()
        for path in sorted(DETERMINISTIC_EXAMPLE_ROOT.iterdir())
        if path.is_dir()
    ]


def create_acceptance_example_paths() -> list[str]:
    if not CREATE_ACCEPTANCE_EXAMPLE_ROOT.exists():
        return []
    return [
        path.as_posix()
        for path in sorted(CREATE_ACCEPTANCE_EXAMPLE_ROOT.iterdir())
        if path.is_dir()
    ]


def live_create_example_paths() -> list[str]:
    if not LIVE_CREATE_EXAMPLE_ROOT.exists():
        return []
    return [
        path.as_posix()
        for path in sorted(LIVE_CREATE_EXAMPLE_ROOT.iterdir())
        if path.is_dir()
    ]


def create_acceptance_live_paths(profile: str) -> list[str]:
    paths = create_acceptance_example_paths()
    if profile == "all":
        return paths
    target = CREATE_ACCEPTANCE_EXAMPLE_ROOT / profile
    return [target.as_posix()] if target.is_dir() else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--codex-live", action="store_true", help="Also run authenticated Codex CLI live smoke against checked-in create-acceptance examples")
    parser.add_argument("--codex-live-profile", default="software-development", help="Profile for --codex-live, or 'all'")
    args = parser.parse_args()

    python = sys.executable
    with tempfile.TemporaryDirectory() as temp_dir:
        create_acceptance_target = Path(temp_dir) / "create-acceptance"
        live_paths = create_acceptance_live_paths(args.codex_live_profile)
        live_create_paths = live_create_example_paths()
        if args.codex_live and not live_paths:
            parser.error(f"No checked-in create-acceptance example found for --codex-live-profile {args.codex_live_profile!r}")
        steps = [
            run_step(
                "static_codex_port_eval",
                [python, "scripts/eval_codex_port.py", "--json", "--max-failures", "120"],
            ),
            run_step(
                "generated_harness_fixture_eval",
                [python, "scripts/eval_generated_harness.py", "--json", *fixture_paths()],
            ),
            run_step(
                "generated_harness_smoke",
                [python, "scripts/smoke_generated_harness.py", "--json", *fixture_paths()],
            ),
            run_step(
                "deterministic_profile_generation",
                [python, "scripts/eval_deterministic_profiles.py", "--json"],
            ),
            run_step(
                "deterministic_example_eval",
                [python, "scripts/eval_generated_harness.py", "--json", *deterministic_example_paths()],
            ),
            run_step(
                "deterministic_example_smoke",
                [python, "scripts/smoke_generated_harness.py", "--json", *deterministic_example_paths()],
            ),
            run_step(
                "deterministic_create_acceptance",
                [
                    python,
                    "scripts/run_create_acceptance.py",
                    create_acceptance_target.as_posix(),
                    "--profile",
                    "software-development",
                    "--project-type",
                    "Python CLI",
                    "--notes",
                    "release gate acceptance",
                    "--json",
                ],
            ),
            run_step(
                "create_acceptance_example_eval",
                [python, "scripts/eval_generated_harness.py", "--json", *create_acceptance_example_paths()],
            ),
            run_step(
                "create_acceptance_example_smoke",
                [python, "scripts/smoke_generated_harness.py", "--json", *create_acceptance_example_paths()],
            ),
            *(
                [
                    run_step(
                        "live_create_example_eval",
                        [python, "scripts/eval_generated_harness.py", "--json", *live_create_paths],
                    ),
                    run_step(
                        "live_create_example_smoke",
                        [python, "scripts/smoke_generated_harness.py", "--json", *live_create_paths],
                    ),
                ]
                if live_create_paths
                else []
            ),
            *(
                [
                    run_step(
                        "create_acceptance_example_codex_live_smoke",
                        [
                            python,
                            "scripts/smoke_generated_harness.py",
                            "--json",
                            "--codex-live",
                            "--prompt",
                            "Reply OK if you loaded this generated harness.",
                            *live_paths,
                        ],
                    )
                ]
                if args.codex_live
                else []
            ),
            run_step(
                "usage_records_validate",
                [python, "scripts/validate_usage_records.py", "--json"],
            ),
            run_step(
                "proof_status",
                [python, "scripts/proof_status.py", "--no-write", "--json"],
            ),
            run_step(
                "unit_and_mutation_tests",
                [python, "-m", "unittest", "discover", "-s", "tests", "-q"],
            ),
            run_step(
                "python_compile",
                [
                    python,
                    "-m",
                    "py_compile",
                    "scripts/check_semantic_alignment.py",
                    "scripts/check_source_freshness.py",
                    "scripts/codex_harness.py",
                    "scripts/capture_live_create_example.py",
                    "scripts/eval_codex_port.py",
                    "scripts/eval_deterministic_profiles.py",
                    "scripts/eval_generated_harness.py",
                    "scripts/generate_minimal_harness.py",
                    "scripts/proof_status.py",
                    "scripts/refresh_create_acceptance_examples.py",
                    "scripts/refresh_deterministic_examples.py",
                    "scripts/record_eval_snapshot.py",
                    "scripts/record_usage_case.py",
                    "scripts/run_create_acceptance.py",
                    "scripts/run_evals.py",
                    "scripts/run_live_example_task_trials.py",
                    "scripts/simulate_create_trigger.py",
                    "scripts/smoke_generated_harness.py",
                    "scripts/validate_usage_records.py",
                    "tests/test_create_acceptance.py",
                    "tests/test_create_trigger_contract.py",
                    "tests/test_codex_harness_cli.py",
                    "tests/test_eval_codex_port.py",
                    "tests/test_generated_harness_contract.py",
                    "tests/test_live_example_task_trials.py",
                    "tests/test_proof_status.py",
                    "tests/test_record_eval_snapshot.py",
                    "tests/test_record_usage_case.py",
                    "tests/test_run_evals.py",
                    "tests/test_semantic_alignment.py",
                    "tests/test_source_freshness.py",
                    "tests/test_validate_usage_records.py",
                ],
            ),
        ]

    status = "pass" if all(step["returncode"] == 0 for step in steps) else "fail"
    payload = {"status": status, "steps": steps}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Eval gate: {status.upper()}")
        for step in steps:
            print(f"- {step['name']}: {step['status'].upper()}")
            if step["returncode"] != 0:
                if step["stdout"]:
                    print(step["stdout"].rstrip())
                if step["stderr"]:
                    print(step["stderr"].rstrip())

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the full Codex Harness Generator eval gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses"
DETERMINISTIC_EXAMPLE_ROOT = REPO_ROOT / "examples" / "deterministic"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    python = sys.executable
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
            "unit_and_mutation_tests",
            [python, "-m", "unittest", "discover", "-s", "tests", "-q"],
        ),
        run_step(
            "python_compile",
            [
                python,
                "-m",
                "py_compile",
                "scripts/eval_codex_port.py",
                "scripts/eval_deterministic_profiles.py",
                "scripts/eval_generated_harness.py",
                "scripts/generate_minimal_harness.py",
                "scripts/refresh_deterministic_examples.py",
                "scripts/run_evals.py",
                "scripts/smoke_generated_harness.py",
                "tests/test_eval_codex_port.py",
                "tests/test_generated_harness_contract.py",
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

#!/usr/bin/env python3
"""Smoke-test the installable codex-harness console command.

This checks the public helper path without relying on an editable install:
install the project into a temporary virtualenv, call the console command, write
a minimal harness, and evaluate that generated harness.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LIMIT = 1200


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd or REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def cleanup_build_artifacts() -> None:
    for name in ("build", "dist"):
        path = REPO_ROOT / name
        if path.exists():
            shutil.rmtree(path)
    for path in REPO_ROOT.glob("*.egg-info"):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def excerpt(text: str) -> str:
    if len(text) <= OUTPUT_LIMIT:
        return text
    return text[:OUTPUT_LIMIT] + "\n...[truncated]"


def build_payload() -> dict:
    steps: list[dict] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        venv = temp_root / "venv"
        generated = temp_root / "generated"
        inspected_generated = temp_root / "inspected-generated"
        demo_generated = temp_root / "demo-generated"
        adoption_report = temp_root / "ADOPTION_PLAN.md"
        usage_records = temp_root / "usage-records"
        usage_report = temp_root / "USAGE_RECORDS.md"
        issue_body = temp_root / "external-usage-issue.md"
        issue_body.write_text(
            "\n".join(
                [
                    "### Domain or project type",
                    "",
                    "install smoke",
                    "",
                    "### Generated harness profile or label",
                    "",
                    "install-smoke issue report",
                    "",
                    "### Evidence type",
                    "",
                    "private-summary",
                    "",
                    "### Outcome",
                    "",
                    "success",
                    "",
                    "### Public-safe task summary",
                    "",
                    "A generated harness was exercised through the install smoke.",
                    "",
                    "### Evidence",
                    "",
                    "- Installed CLI generated and validated a harness.",
                    "- Installed CLI converted a copied-harness eval into usage evidence.",
                    "",
                    "### Verification performed",
                    "",
                    "- codex-harness validate passed.",
                    "- codex-harness local-eval passed.",
                    "",
                    "### Privacy review",
                    "",
                    "Public-safe install-smoke issue body only; no secrets, personal data, private paths, or raw logs.",
                    "",
                    "### Limitations",
                    "",
                    "- Single synthetic install smoke.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        commands = [
            ("create_venv", [sys.executable, "-m", "venv", "--system-site-packages", venv.as_posix()]),
            (
                "install_package",
                [
                    (venv / "bin" / "python").as_posix(),
                    "-m",
                    "pip",
                    "install",
                    "--no-build-isolation",
                    "--no-deps",
                    ".",
                ],
            ),
            ("profiles", [(venv / "bin" / "codex-harness").as_posix(), "profiles", "--json"]),
            ("doctor", [(venv / "bin" / "codex-harness").as_posix(), "doctor", "--json"]),
            (
                "init",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "init",
                    generated.as_posix(),
                    "--brief",
                    "RAG app with prompts, evals, and retrieval checks",
                    "--project-name",
                    "Install Smoke RAG Harness",
                    "--force",
                    "--json",
                ],
            ),
            (
                "demo_capture",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "demo-capture",
                    demo_generated.as_posix(),
                    "--brief",
                    "RAG app with prompts, evals, and retrieval checks",
                    "--project-name",
                    "Install Smoke Demo Harness",
                    "--target-label",
                    "install-smoke-demo",
                    "--force",
                    "--json",
                ],
            ),
            ("validate", [(venv / "bin" / "codex-harness").as_posix(), "validate", generated.as_posix(), "--json"]),
            ("inspect", [(venv / "bin" / "codex-harness").as_posix(), "inspect", generated.as_posix(), "--json"]),
            (
                "adoption_plan",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "adoption-plan",
                    generated.as_posix(),
                    "--source-label",
                    "install-smoke generated harness",
                    "--report",
                    adoption_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "init_from_project",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "init",
                    inspected_generated.as_posix(),
                    "--from-project",
                    generated.as_posix(),
                    "--project-name",
                    "Install Smoke Inspected Harness",
                    "--source-label",
                    "install-smoke generated harness",
                    "--target-label",
                    "install-smoke-inspected",
                    "--force",
                    "--json",
                ],
            ),
            (
                "record_task_trial",
                [
                    (venv / "bin" / "python").as_posix(),
                    (generated / "scripts" / "record-task-trial.py").as_posix(),
                    "--task",
                    "install smoke generated-harness task",
                    "--outcome",
                    "success",
                    "--evidence",
                    "public-safe install smoke artifact",
                    "--verification",
                    "codex-harness validate and local-eval",
                    "--privacy-review",
                    "synthetic install-smoke evidence only",
                    "--limitations",
                    "single synthetic install smoke",
                ],
            ),
            ("local_eval", [(venv / "bin" / "codex-harness").as_posix(), "local-eval", generated.as_posix(), "--json"]),
            (
                "usage_from_harness",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-from-harness",
                    generated.as_posix(),
                    "--slug",
                    "install-smoke",
                    "--title",
                    "Install smoke generated harness",
                    "--domain",
                    "install smoke",
                    "--harness-label",
                    "install-smoke generated harness",
                    "--evidence-type",
                    "synthetic",
                    "--privacy-review",
                    "synthetic install-smoke evidence only",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_report.as_posix(),
                    "--force",
                    "--json",
                ],
            ),
            (
                "usage_from_issue",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-from-issue",
                    issue_body.as_posix(),
                    "--slug",
                    "install-smoke-issue",
                    "--title",
                    "Install smoke issue report",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_report.as_posix(),
                    "--force",
                    "--json",
                ],
            ),
            ("migration_audit", [(venv / "bin" / "codex-harness").as_posix(), "migration-audit", generated.as_posix(), "--json"]),
            ("eval", [(venv / "bin" / "codex-harness").as_posix(), "eval", generated.as_posix()]),
        ]

        try:
            for name, command in commands:
                completed = run(command)
                step = {
                    "name": name,
                    "command": command,
                    "returncode": completed.returncode,
                    "status": "pass" if completed.returncode == 0 else "fail",
                    "stdout": excerpt(completed.stdout),
                    "stderr": excerpt(completed.stderr),
                }
                if name == "profiles" and completed.returncode == 0:
                    profile_payload = json.loads(completed.stdout)
                    step["profile_count"] = profile_payload.get("profile_count")
                    if profile_payload.get("profile_count") != 20:
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nExpected 20 profiles from installed CLI."
                steps.append(step)
                if step["status"] == "fail":
                    break
        finally:
            cleanup_build_artifacts()

    return {
        "status": "pass" if all(step["status"] == "pass" for step in steps) else "fail",
        "steps": steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = build_payload()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Installable CLI smoke: {payload['status'].upper()}")
        for step in payload["steps"]:
            print(f"- {step['name']}: {step['status'].upper()}")
            if step["status"] == "fail":
                if step["stdout"]:
                    print(step["stdout"].rstrip())
                if step["stderr"]:
                    print(step["stderr"].rstrip())

    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

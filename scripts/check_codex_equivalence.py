#!/usr/bin/env python3
"""Check and report the Codex-native equivalence surface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path.cwd().resolve()
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "CODEX_EQUIVALENCE_MATRIX.md"

CAPABILITIES = [
    {
        "name": "Project instruction contract",
        "original_need": "Durable project-level operating instructions.",
        "codex_surface": "AGENTS.md plus generated AGENTS.md files.",
        "evidence_paths": ["AGENTS.md", "scripts/generate_minimal_harness.py", "tests/test_generated_harness_contract.py"],
        "commands": ["codex-harness validate <generated-harness>"],
    },
    {
        "name": "Codex configuration",
        "original_need": "Portable runtime configuration and permission posture.",
        "codex_surface": ".codex/config.toml, permission profiles, and config templates.",
        "evidence_paths": [".codex/config.toml", "Docs/Templates/Core/codex-config-toml.md", "scripts/eval_codex_port.py"],
        "commands": ["python scripts/eval_codex_port.py"],
    },
    {
        "name": "Subagents",
        "original_need": "Specialized workers for intake, architecture, generation, validation, and upgrade work.",
        "codex_surface": ".codex/agents/*.toml plus generated reviewer agents.",
        "evidence_paths": [".codex/agents", "Docs/Templates/Agents", "tests/test_eval_codex_port.py"],
        "commands": ["codex-harness validate <generated-harness>"],
    },
    {
        "name": "Skills",
        "original_need": "Reusable triggered workflows for create, validate, update, and upgrade paths.",
        "codex_surface": ".agents/skills/*/SKILL.md plus generated health-check skills.",
        "evidence_paths": [".agents/skills", "scripts/eval_codex_port.py", "tests/test_eval_codex_port.py"],
        "commands": ["python scripts/eval_codex_port.py"],
    },
    {
        "name": "Profile catalog",
        "original_need": "Domain-specific starting points instead of one generic setup.",
        "codex_surface": "20 deterministic starter profiles with brief-based recommendation.",
        "evidence_paths": ["scripts/profile_catalog.py", "Docs/StarterProfiles", "tests/test_profile_catalog.py"],
        "commands": ["codex-harness profiles", "codex-harness recommend <brief>"],
    },
    {
        "name": "Generation",
        "original_need": "Create a ready-to-use harness directory.",
        "codex_surface": "codex-harness quickstart/init/generate/brief-acceptance/create-acceptance flows.",
        "evidence_paths": ["scripts/generate_minimal_harness.py", "scripts/run_quickstart.py", "scripts/run_brief_acceptance.py", "examples/brief-acceptance"],
        "commands": ["codex-harness quickstart <target> --brief <brief>", "codex-harness init <target> --brief <brief>", "codex-harness brief-acceptance <target> --brief <brief>"],
    },
    {
        "name": "Validation",
        "original_need": "Verify generated environments before trusting them.",
        "codex_surface": "Generated local checks, repo evals, smoke tests, and validation reports.",
        "evidence_paths": ["scripts/validate_generated_harness.py", "scripts/eval_generated_harness.py", "scripts/smoke_generated_harness.py"],
        "commands": ["codex-harness validate <generated-harness>", "codex-harness gate"],
    },
    {
        "name": "Existing-project adoption",
        "original_need": "Adopt a harness into an existing project without overwriting work.",
        "codex_surface": "Project inspection, adoption plans, add-only copy scripts, and migration audit.",
        "evidence_paths": ["scripts/inspect_project.py", "scripts/plan_project_adoption.py", "scripts/migration_audit.py"],
        "commands": ["codex-harness inspect <path>", "codex-harness adoption-plan <path>", "codex-harness migration-audit <path>"],
    },
    {
        "name": "Copied-harness autonomy",
        "original_need": "A copied harness should keep working away from the generator repo.",
        "codex_surface": "Generated local check, local eval report, task-trial recorder, improvement recorder, and public usage report exporter.",
        "evidence_paths": [
            "tests/test_generated_harness_contract.py",
            "examples/deterministic/software-development/scripts/run-harness-evals.py",
            "examples/deterministic/software-development/scripts/export-public-usage-report.py",
        ],
        "commands": ["codex-harness local-eval <generated-harness>"],
    },
    {
        "name": "High-risk guardrails",
        "original_need": "Domain guardrails for risky work.",
        "codex_surface": "Profile-specific guardrails and evaluator failures for missing boundaries.",
        "evidence_paths": ["scripts/generate_minimal_harness.py", "tests/test_generated_harness_contract.py", "Docs/DomainLibrary"],
        "commands": ["python -m unittest tests.test_generated_harness_contract -q"],
    },
    {
        "name": "Usage evidence",
        "original_need": "Record whether generated harnesses actually help with real tasks.",
        "codex_surface": "Usage records, validation thresholds, prepared pilots, pilot packs, and pilot campaigns.",
        "evidence_paths": [
            "Docs/Environment/USAGE_RECORDS.md",
            "Docs/Environment/USAGE_GAPS.md",
            "Docs/Environment/PILOT_CAMPAIGN.md",
            "scripts/prepare_pilot.py",
            "scripts/record_usage_case.py",
        ],
        "commands": ["codex-harness prepare-pilot <target>", "codex-harness usage-validate", "codex-harness usage-gaps", "codex-harness pilot-campaign"],
    },
    {
        "name": "Release proof",
        "original_need": "A single readiness view before public claims.",
        "codex_surface": "Proof status, proof matrix, generated-surface refresh, eval trends, source freshness, and semantic alignment.",
        "evidence_paths": [
            "Docs/Environment/PROOF_STATUS.md",
            "Docs/Environment/PROOF_MATRIX.md",
            "scripts/proof_status.py",
            "scripts/refresh_generated_surfaces.py",
        ],
        "commands": ["codex-harness refresh-examples", "codex-harness proof-status", "codex-harness gate"],
    },
]


def command_names() -> set[str]:
    completed = subprocess.run(
        [sys.executable, "scripts/codex_harness.py", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    text = completed.stdout + "\n" + completed.stderr
    names = set()
    for capability in CAPABILITIES:
        for command in capability["commands"]:
            parts = command.split()
            if parts and parts[0] == "codex-harness" and len(parts) > 1:
                names.add(parts[1])
    return {name for name in names if name in text}


def build_payload() -> dict:
    exposed_commands = command_names()
    capabilities = []
    failures = []
    for capability in CAPABILITIES:
        missing_paths = [path for path in capability["evidence_paths"] if not (REPO_ROOT / path).exists()]
        missing_commands = []
        for command in capability["commands"]:
            parts = command.split()
            if parts and parts[0] == "codex-harness" and len(parts) > 1 and parts[1] not in exposed_commands:
                missing_commands.append(parts[1])
        status = "pass" if not missing_paths and not missing_commands else "fail"
        if status == "fail":
            failures.append(
                {
                    "name": capability["name"],
                    "missing_paths": missing_paths,
                    "missing_commands": sorted(set(missing_commands)),
                }
            )
        capabilities.append({**capability, "status": status, "missing_paths": missing_paths, "missing_commands": sorted(set(missing_commands))})
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if not failures else "fail",
        "capability_count": len(capabilities),
        "failure_count": len(failures),
        "capabilities": capabilities,
        "failures": failures,
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Codex Equivalence Matrix",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        "",
        "This matrix maps the earlier harness-generator responsibilities to the",
        "Codex-native surface in this repository. It proves checked-in parity of",
        "structure and workflow coverage, not external adoption or production",
        "performance.",
        "",
        "| Capability | Status | Original responsibility | Codex-native surface | Evidence | Commands |",
        "|---|---|---|---|---|---|",
    ]
    for capability in payload["capabilities"]:
        evidence = "<br>".join(f"`{path}`" for path in capability["evidence_paths"])
        commands = "<br>".join(f"`{command}`" for command in capability["commands"])
        lines.append(
            "| {name} | {status} | {original} | {surface} | {evidence} | {commands} |".format(
                name=capability["name"],
                status=capability["status"].upper(),
                original=capability["original_need"],
                surface=capability["codex_surface"],
                evidence=evidence,
                commands=commands,
            )
        )
    if payload["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in payload["failures"]:
            lines.append(f"- {failure['name']}: missing paths={failure['missing_paths']} missing commands={failure['missing_commands']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload()
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Codex equivalence: {payload['status'].upper()} ({payload['capability_count']} capabilities)")
        for capability in payload["capabilities"]:
            print(f"- {capability['name']}: {capability['status'].upper()}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

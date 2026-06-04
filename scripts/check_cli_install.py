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
SOURCE_COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "build",
    "dist",
    "*.egg-info",
)


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


def copy_install_source(destination: Path) -> None:
    """Copy the repo to an isolated source tree before package installation."""
    shutil.copytree(REPO_ROOT, destination, ignore=SOURCE_COPY_IGNORE)


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
        quickstart_generated = temp_root / "quickstart-generated"
        pilot_generated = temp_root / "pilot-generated"
        next_pilot_generated = temp_root / "next-pilot-generated"
        inspected_generated = temp_root / "inspected-generated"
        demo_generated = temp_root / "demo-generated"
        adoption_report = temp_root / "ADOPTION_PLAN.md"
        adoption_blueprint = temp_root / "adoption-blueprint"
        adoption_copy_script = temp_root / "copy-adds.sh"
        equivalence_report = temp_root / "CODEX_EQUIVALENCE_MATRIX.md"
        evidence_packet = temp_root / "HARNESS_EVIDENCE_PACKET.md"
        public_usage_report = temp_root / "PUBLIC_USAGE_REPORT.md"
        pilot_pack = temp_root / "EXTERNAL_PILOT_PACK.md"
        pilot_issue = temp_root / "EXTERNAL_USAGE_ISSUE_DRAFT.md"
        prepared_pilot_pack = temp_root / "PREPARED_EXTERNAL_PILOT_PACK.md"
        prepared_pilot_issue = temp_root / "PREPARED_EXTERNAL_USAGE_ISSUE_DRAFT.md"
        prepared_pilot_record = temp_root / "PREPARED_EXTERNAL_PILOT_RECORD.json"
        next_pilot_pack = temp_root / "NEXT_EXTERNAL_PILOT_PACK.md"
        next_pilot_issue = temp_root / "NEXT_EXTERNAL_USAGE_ISSUE_DRAFT.md"
        pilot_batch_root = temp_root / "pilot-batch"
        pilot_batch_out = temp_root / "pilot-batch-packs"
        pilot_records = temp_root / "pilot-records"
        pilot_board_report = temp_root / "PILOT_BOARD.md"
        pilot_outreach_report = temp_root / "PILOT_OUTREACH.md"
        pilot_handoff_root = temp_root / "pilot-handoffs"
        pilot_handoff_audit_report = temp_root / "PILOT_HANDOFF_AUDIT.md"
        pilot_github_issues_root = temp_root / "pilot-github-issues"
        pilot_github_issues_report = temp_root / "PILOT_GITHUB_ISSUES.md"
        pilot_github_sync_report = temp_root / "PILOT_GITHUB_SYNC.md"
        pilot_next_action_report = temp_root / "PILOT_NEXT_ACTION.md"
        beta_exit_audit_report = temp_root / "BETA_EXIT_AUDIT.md"
        usage_records = temp_root / "usage-records"
        usage_report = temp_root / "USAGE_RECORDS.md"
        usage_gaps_report = temp_root / "USAGE_GAPS.md"
        pilot_campaign_report = temp_root / "PILOT_CAMPAIGN.md"
        proof_next_report = temp_root / "PROOF_NEXT.md"
        migration_plan_report = temp_root / "CODEX_MIGRATION_PLAN.md"
        migration_packet = temp_root / "migration-packet"
        issue_body = temp_root / "external-usage-issue.md"
        linked_pilot_issue_body = temp_root / "linked-pilot-usage-issue.md"
        install_source = temp_root / "source"
        copy_install_source(install_source)
        issue_body.write_text(
            "\n".join(
                [
                    "### Pilot or usage-record slug",
                    "",
                    "install-smoke-issue",
                    "",
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
                    "### Source type",
                    "",
                    "self-dogfood",
                    "",
                    "### Generation path",
                    "",
                    "installed-quickstart",
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
        linked_pilot_issue_body.write_text(
            "\n".join(
                [
                    "### Pilot or usage-record slug",
                    "",
                    "llm-app-pilot",
                    "",
                    "### Domain or project type",
                    "",
                    "LLM app",
                    "",
                    "### Generated harness profile or label",
                    "",
                    "LLM App Workspace Pilot",
                    "",
                    "### Evidence type",
                    "",
                    "private-summary",
                    "",
                    "### Source type",
                    "",
                    "external",
                    "",
                    "### Generation path",
                    "",
                    "installed-quickstart",
                    "",
                    "### Outcome",
                    "",
                    "success",
                    "",
                    "### Public-safe task summary",
                    "",
                    "A prepared pilot was converted through the installed CLI smoke workflow.",
                    "",
                    "### Evidence",
                    "",
                    "- Installed CLI prepared a matching external pilot record.",
                    "- Installed CLI converted the reporter issue into checked usage evidence.",
                    "",
                    "### Verification performed",
                    "",
                    "- usage-from-issue returned a passing linked pilot update payload.",
                    "- pilot-board validated the converted usage record reference.",
                    "",
                    "### Privacy review",
                    "",
                    "Public-safe install-smoke linked conversion only; no secrets, private paths, personal data, or raw logs.",
                    "",
                    "### Limitations",
                    "",
                    "- Single installed CLI linked-conversion smoke.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        fake_gh = temp_root / "fake-gh"
        fake_gh_payload = {
            "number": 12,
            "title": "External usage pilot: LLM app pilot",
            "url": "https://github.com/example/repo/issues/12",
            "state": "OPEN",
            "body": linked_pilot_issue_body.read_text(encoding="utf-8"),
        }
        fake_gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json\n"
            f"print(json.dumps({json.dumps(fake_gh_payload)}))\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)

        commands = [
            ("create_venv", [sys.executable, "-m", "venv", venv.as_posix()], None),
            (
                "install_package",
                [(venv / "bin" / "python").as_posix(), "-m", "pip", "install", "."],
                install_source,
            ),
            ("profiles", [(venv / "bin" / "codex-harness").as_posix(), "profiles", "--json"], None),
            ("doctor", [(venv / "bin" / "codex-harness").as_posix(), "doctor", "--json"], None),
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
                "quickstart",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "quickstart",
                    quickstart_generated.as_posix(),
                    "--brief",
                    "RAG app with prompts, evals, and retrieval checks",
                    "--project-name",
                    "Install Smoke Quickstart Harness",
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
            (
                "prepare_pilot",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "prepare-pilot",
                    pilot_generated.as_posix(),
                    "--brief",
                    "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task",
                    "--project-name",
                    "Install Smoke External Pilot Harness",
                    "--domain",
                    "install smoke pilot",
                    "--slug",
                    "install-smoke-prepared-pilot",
                    "--title",
                    "Install smoke prepared pilot",
                    "--out",
                    prepared_pilot_pack.as_posix(),
                    "--issue-out",
                    prepared_pilot_issue.as_posix(),
                    "--pilot-record-out",
                    prepared_pilot_record.as_posix(),
                    "--pilot-notes",
                    "install smoke direct pilot record",
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
                    "--blueprint-out",
                    adoption_blueprint.as_posix(),
                    "--copy-script",
                    adoption_copy_script.as_posix(),
                    "--json",
                ],
            ),
            (
                "equivalence",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "equivalence",
                    "--report",
                    equivalence_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "upstream_drift",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "upstream-drift",
                    "--upstream",
                    "HEAD",
                    "--target",
                    "HEAD",
                    "--no-write",
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
                "public_usage_report",
                [
                    (venv / "bin" / "python").as_posix(),
                    (generated / "scripts" / "export-public-usage-report.py").as_posix(),
                    "--out",
                    public_usage_report.as_posix(),
                    "--source-type",
                    "self-dogfood",
                    "--generation-path",
                    "installed-init-brief",
                    "--json",
                ],
            ),
            (
                "evidence_packet",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "evidence-packet",
                    generated.as_posix(),
                    "--out",
                    evidence_packet.as_posix(),
                    "--harness-label",
                    "install-smoke generated harness",
                    "--json",
                ],
            ),
            (
                "pilot_pack",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-pack",
                    generated.as_posix(),
                    "--out",
                    pilot_pack.as_posix(),
                    "--issue-out",
                    pilot_issue.as_posix(),
                    "--harness-label",
                    "install-smoke generated harness",
                    "--domain",
                    "install smoke",
                    "--slug",
                    "install-smoke-pilot",
                    "--title",
                    "Install smoke pilot",
                    "--source-type",
                    "self-dogfood",
                    "--generation-path",
                    "installed-init-brief",
                    "--prefill-from-trials",
                    "--json",
                ],
            ),
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
                    "--source-type",
                    "self-dogfood",
                    "--generation-path",
                    "installed-init-brief",
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
                "usage_from_issue_lint",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-from-issue",
                    issue_body.as_posix(),
                    "--slug",
                    "install-smoke-issue-lint",
                    "--title",
                    "Install smoke issue lint",
                    "--source-type",
                    "self-dogfood",
                    "--generation-path",
                    "installed-quickstart",
                    "--lint-only",
                    "--json",
                ],
            ),
            (
                "usage_from_issue_preview",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-from-issue",
                    issue_body.as_posix(),
                    "--slug",
                    "install-smoke-issue-preview",
                    "--title",
                    "Install smoke issue preview",
                    "--source-type",
                    "self-dogfood",
                    "--generation-path",
                    "installed-quickstart",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_report.as_posix(),
                    "--no-write",
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
                    "--source-type",
                    "self-dogfood",
                    "--generation-path",
                    "installed-quickstart",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_report.as_posix(),
                    "--force",
                    "--json",
                ],
            ),
            (
                "prepare_next_pilot",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "prepare-next-pilot",
                    next_pilot_generated.as_posix(),
                    "--record-dir",
                    usage_records.as_posix(),
                    "--out",
                    next_pilot_pack.as_posix(),
                    "--issue-out",
                    next_pilot_issue.as_posix(),
                    "--pilot-record-dir",
                    pilot_records.as_posix(),
                    "--force",
                    "--json",
                ],
            ),
            (
                "prepare_pilot_batch_dry_run",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "prepare-pilot-batch",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--target-root",
                    pilot_batch_root.as_posix(),
                    "--out-dir",
                    pilot_batch_out.as_posix(),
                    "--pilot-record-dir",
                    pilot_records.as_posix(),
                    "--max-pilots",
                    "2",
                    "--dry-run",
                    "--json",
                ],
            ),
            (
                "pilot_board",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-board",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--report",
                    pilot_board_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_update",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-update",
                    "llm-app-pilot",
                    "--status",
                    "invited",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--report",
                    pilot_board_report.as_posix(),
                    "--notes",
                    "opened public pilot issue https://github.com/example/repo/issues/12",
                    "--json",
                ],
            ),
            (
                "pilot_outreach",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-outreach",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--out",
                    pilot_outreach_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_handoff",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-handoff",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--out",
                    pilot_handoff_root.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_handoff_audit",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-handoff-audit",
                    "--handoff-dir",
                    pilot_handoff_root.as_posix(),
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--report",
                    pilot_handoff_audit_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_github_issues",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-github-issues",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--out-dir",
                    pilot_github_issues_root.as_posix(),
                    "--report",
                    pilot_github_issues_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_github_sync",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-github-sync",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--report",
                    pilot_github_sync_report.as_posix(),
                    "--followup-dir",
                    (temp_root / "pilot-github-followups").as_posix(),
                    "--gh-bin",
                    fake_gh.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_next_action",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-next-action",
                    "--record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--sync-report",
                    pilot_github_sync_report.as_posix(),
                    "--report",
                    pilot_next_action_report.as_posix(),
                    "--followup-dir",
                    (temp_root / "pilot-github-followups").as_posix(),
                    "--gh-bin",
                    fake_gh.as_posix(),
                    "--json",
                ],
            ),
            (
                "usage_from_issue_pilot_conversion",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-from-issue",
                    linked_pilot_issue_body.as_posix(),
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_report.as_posix(),
                    "--pilot-record-dir",
                    pilot_records.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "usage_from_github_issue_lint",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-from-github-issue",
                    "12",
                    "--repo",
                    "example/repo",
                    "--gh-bin",
                    fake_gh.as_posix(),
                    "--include-comments",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_report.as_posix(),
                    "--pilot-record-dir",
                    pilot_records.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--lint-only",
                    "--json",
                ],
            ),
            (
                "usage_gaps",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "usage-gaps",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--report",
                    usage_gaps_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "beta_exit_audit",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "beta-exit-audit",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--pilot-record-dir",
                    pilot_records.as_posix(),
                    "--usage-record-dir",
                    usage_records.as_posix(),
                    "--report",
                    beta_exit_audit_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "pilot_campaign",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "pilot-campaign",
                    "--record-dir",
                    usage_records.as_posix(),
                    "--out",
                    pilot_campaign_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "proof_next",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "proof-next",
                    next_pilot_generated.as_posix(),
                    "--record-dir",
                    usage_records.as_posix(),
                    "--pilot-record-dir",
                    pilot_records.as_posix(),
                    "--pilot-board-report",
                    pilot_board_report.as_posix(),
                    "--usage-report",
                    usage_report.as_posix(),
                    "--pilot-pack-out",
                    next_pilot_pack.as_posix(),
                    "--issue-out",
                    next_pilot_issue.as_posix(),
                    "--report",
                    proof_next_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "migration_audit",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "migration-audit",
                    generated.as_posix(),
                    "--report",
                    migration_plan_report.as_posix(),
                    "--json",
                ],
            ),
            (
                "prepare_migration",
                [
                    (venv / "bin" / "codex-harness").as_posix(),
                    "prepare-migration",
                    generated.as_posix(),
                    migration_packet.as_posix(),
                    "--source-label",
                    "install smoke generated harness",
                    "--generated",
                    "2026-06-04T12:00:00Z",
                    "--json",
                ],
            ),
            ("eval", [(venv / "bin" / "codex-harness").as_posix(), "eval", generated.as_posix()]),
        ]

        try:
            for item in commands:
                name = item[0]
                command = item[1]
                cwd = item[2] if len(item) > 2 else None
                completed = run(command, cwd=cwd)
                step = {
                    "name": name,
                    "command": command,
                    "cwd": cwd.as_posix() if cwd else ".",
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
                if name == "usage_from_issue_lint" and completed.returncode == 0:
                    lint_payload = json.loads(completed.stdout)
                    if lint_payload.get("status") != "pass" or lint_payload.get("readiness") != "conversion-ready":
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nIssue lint payload did not prove a conversion-ready issue body."
                if name == "prepare_pilot" and completed.returncode == 0:
                    prepare_payload = json.loads(completed.stdout)
                    pilot_record = prepare_payload.get("pilot_record") or {}
                    if (
                        prepare_payload.get("status") != "pass"
                        or pilot_record.get("status") != "pass"
                        or not prepared_pilot_record.exists()
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nPrepare-pilot did not write a passing direct pilot-board record."
                if name == "upstream_drift" and completed.returncode == 0:
                    drift_payload = json.loads(completed.stdout)
                    if drift_payload.get("status") != "pass" or drift_payload.get("ahead_behind", {}).get("upstream_only") != 0:
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nUpstream drift smoke did not prove a clean self-compare."
                if name == "prepare_migration" and completed.returncode == 0:
                    migration_payload = json.loads(completed.stdout)
                    if (
                        migration_payload.get("status") != "pass"
                        or not (migration_packet / "README.md").exists()
                        or not (migration_packet / "copy-codex-harness-adds.sh").exists()
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nPrepare-migration did not write a complete migration packet."
                if name == "prepare_pilot_batch_dry_run" and completed.returncode == 0:
                    batch_payload = json.loads(completed.stdout)
                    if (
                        batch_payload.get("status") != "pass"
                        or batch_payload.get("mode") != "dry-run"
                        or batch_payload.get("selected_count", 0) < 1
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nPilot batch dry-run did not return a passing planned batch."
                if name == "pilot_outreach" and completed.returncode == 0:
                    outreach_payload = json.loads(completed.stdout)
                    if (
                        outreach_payload.get("status") != "pass"
                        or outreach_payload.get("readiness") != "outreach-ready"
                        or outreach_payload.get("outreach_count", 0) < 1
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nPilot outreach did not return a passing outreach-ready packet."
                if name == "pilot_handoff" and completed.returncode == 0:
                    handoff_payload = json.loads(completed.stdout)
                    if (
                        handoff_payload.get("status") != "pass"
                        or handoff_payload.get("readiness") != "handoff-ready"
                        or handoff_payload.get("handoff_count", 0) < 1
                        or not (pilot_handoff_root / "llm-app-pilot" / "README.md").exists()
                        or not (pilot_handoff_root / "llm-app-pilot" / "REPORTER_HANDOFF.md").exists()
                        or not (pilot_handoff_root / "llm-app-pilot" / "USAGE_REPORT_DRAFT.md").exists()
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nPilot handoff did not write a passing shareable handoff folder."
                if name == "pilot_handoff_audit" and completed.returncode == 0:
                    handoff_audit_payload = json.loads(completed.stdout)
                    if (
                        handoff_audit_payload.get("status") != "pass"
                        or handoff_audit_payload.get("readiness") != "handoff-audit-ready"
                        or handoff_audit_payload.get("handoff_count", 0) < 1
                        or not pilot_handoff_audit_report.exists()
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nPilot handoff audit did not prove reporter-ready handoff folders."
                if name == "usage_from_issue_pilot_conversion" and completed.returncode == 0:
                    conversion_payload = json.loads(completed.stdout)
                    pilot_update = conversion_payload.get("pilot_update") or {}
                    if (
                        conversion_payload.get("status") != "pass"
                        or pilot_update.get("status") != "pass"
                        or pilot_update.get("board_status") != "pass"
                        or (pilot_update.get("record") or {}).get("status") != "converted"
                        or (pilot_update.get("record") or {}).get("usage_record") != "llm-app-pilot"
                    ):
                        step["status"] = "fail"
                        step["returncode"] = 1
                        step["stderr"] += "\nLinked pilot conversion payload did not prove a validated conversion."
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

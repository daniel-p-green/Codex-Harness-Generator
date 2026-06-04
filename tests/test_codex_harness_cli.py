import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "scripts" / "codex_harness.py"

spec = importlib.util.spec_from_file_location("codex_harness", CLI_PATH)
codex_harness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(codex_harness)


class CodexHarnessCliTests(unittest.TestCase):
    def test_pyproject_exposes_codex_harness_console_script(self):
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn('name = "codex-harness-generator"', pyproject)
        self.assertIn('codex-harness = "scripts.codex_harness:main"', pyproject)
        self.assertIn('packages = ["scripts"]', pyproject)
        self.assertTrue((REPO_ROOT / "scripts" / "__init__.py").exists())

    def run_cli(self, argv):
        with patch.object(codex_harness.sys, "executable", "/usr/bin/python3"):
            with patch.object(codex_harness.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
                status = codex_harness.main(argv)
        self.assertEqual(0, status)
        return run.call_args.args[0], run.call_args.kwargs

    def test_profiles_delegates_to_generator(self):
        command, kwargs = self.run_cli(["profiles"])

        self.assertEqual(["/usr/bin/python3", "scripts/generate_minimal_harness.py", "--list-profiles"], command)
        self.assertEqual(codex_harness.REPO_ROOT, kwargs["cwd"])

    def test_init_without_brief_delegates_to_generator(self):
        command, _ = self.run_cli(
            [
                "init",
                "/tmp/example",
                "--profile",
                "knowledge-work",
                "--project-name",
                "Research Hub",
                "--force",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/generate_minimal_harness.py",
                "/tmp/example",
                "--profile",
                "knowledge-work",
                "--project-name",
                "Research Hub",
                "--force",
            ],
            command,
        )

    def test_init_with_brief_delegates_to_brief_acceptance(self):
        command, _ = self.run_cli(
            [
                "init",
                "/tmp/example",
                "--brief",
                "RAG app with prompts and evals",
                "--project-name",
                "RAG Harness",
                "--notes",
                "trial",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "examples/brief",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_brief_acceptance.py",
                "/tmp/example",
                "--brief",
                "RAG app with prompts and evals",
                "--project-name",
                "RAG Harness",
                "--notes",
                "trial",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "examples/brief",
                "--force",
                "--json",
            ],
            command,
        )

    def test_init_from_project_delegates_to_inspected_acceptance(self):
        command, _ = self.run_cli(
            [
                "init",
                "/tmp/generated",
                "--from-project",
                "/tmp/source",
                "--project-name",
                "Source Project",
                "--notes",
                "inspect trial",
                "--limit",
                "2",
                "--max-files",
                "25",
                "--allow-low-confidence",
                "--target-label",
                "tmp/generated",
                "--source-label",
                "public source",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_inspected_acceptance.py",
                "/tmp/generated",
                "--from-project",
                "/tmp/source",
                "--project-name",
                "Source Project",
                "--notes",
                "inspect trial",
                "--limit",
                "2",
                "--max-files",
                "25",
                "--allow-low-confidence",
                "--target-label",
                "tmp/generated",
                "--source-label",
                "public source",
                "--force",
                "--json",
            ],
            command,
        )

    def test_quickstart_delegates_to_quickstart_runner(self):
        command, _ = self.run_cli(
            [
                "quickstart",
                "/tmp/quick",
                "--brief",
                "RAG app with prompts and evals",
                "--project-name",
                "Quick Harness",
                "--notes",
                "trial",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "tmp/quick",
                "--force",
                "--min-score",
                "95",
                "--min-successes",
                "1",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_quickstart.py",
                "/tmp/quick",
                "--brief",
                "RAG app with prompts and evals",
                "--project-name",
                "Quick Harness",
                "--notes",
                "trial",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "tmp/quick",
                "--force",
                "--min-score",
                "95",
                "--min-successes",
                "1",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_prepare_pilot_delegates_to_pilot_preparer(self):
        command, _ = self.run_cli(
            [
                "prepare-pilot",
                "/tmp/pilot",
                "--brief",
                "RAG app with prompts and evals",
                "--project-name",
                "Pilot Harness",
                "--notes",
                "external pilot",
                "--domain",
                "LLM app",
                "--slug",
                "external-rag-pilot",
                "--title",
                "External RAG pilot",
                "--source-type",
                "external",
                "--generation-path",
                "installed-quickstart",
                "--harness-label",
                "public pilot harness",
                "--out",
                "/tmp/PILOT_PACK.md",
                "--issue-out",
                "/tmp/ISSUE.md",
                "--min-successes",
                "2",
                "--min-score",
                "95",
                "--target-label",
                "tmp/pilot",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--generated-date",
                "2026-06-04",
                "--created",
                "2026-06-04T12:00:00Z",
                "--generated",
                "2026-06-04T12:00:00Z",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/prepare_pilot.py",
                "/tmp/pilot",
                "--brief",
                "RAG app with prompts and evals",
                "--project-name",
                "Pilot Harness",
                "--notes",
                "external pilot",
                "--domain",
                "LLM app",
                "--slug",
                "external-rag-pilot",
                "--title",
                "External RAG pilot",
                "--source-type",
                "external",
                "--generation-path",
                "installed-quickstart",
                "--harness-label",
                "public pilot harness",
                "--out",
                "/tmp/PILOT_PACK.md",
                "--issue-out",
                "/tmp/ISSUE.md",
                "--min-successes",
                "2",
                "--min-score",
                "95",
                "--target-label",
                "tmp/pilot",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--generated-date",
                "2026-06-04",
                "--created",
                "2026-06-04T12:00:00Z",
                "--generated",
                "2026-06-04T12:00:00Z",
                "--force",
                "--json",
            ],
            command,
        )

    def test_prepare_next_pilot_delegates_to_gap_based_preparer(self):
        command, _ = self.run_cli(
            [
                "prepare-next-pilot",
                "/tmp/next-pilot",
                "--record-dir",
                "/tmp/records",
                "--index",
                "2",
                "--brief",
                "Security audit pilot",
                "--project-name",
                "Next Pilot Harness",
                "--notes",
                "gap selected pilot",
                "--domain",
                "security audit",
                "--slug",
                "security-audit-pilot",
                "--title",
                "Security audit pilot",
                "--source-type",
                "external",
                "--generation-path",
                "installed-quickstart",
                "--harness-label",
                "next pilot harness",
                "--out",
                "/tmp/NEXT_PILOT_PACK.md",
                "--issue-out",
                "/tmp/NEXT_ISSUE.md",
                "--min-successes",
                "2",
                "--min-score",
                "95",
                "--target-label",
                "tmp/next-pilot",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--generated-date",
                "2026-06-04",
                "--created",
                "2026-06-04T12:00:00Z",
                "--generated",
                "2026-06-04T12:00:00Z",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--pilot-status",
                "invited",
                "--pilot-notes",
                "sent to reporter",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/prepare_next_pilot.py",
                "/tmp/next-pilot",
                "--record-dir",
                "/tmp/records",
                "--index",
                "2",
                "--brief",
                "Security audit pilot",
                "--project-name",
                "Next Pilot Harness",
                "--notes",
                "gap selected pilot",
                "--domain",
                "security audit",
                "--slug",
                "security-audit-pilot",
                "--title",
                "Security audit pilot",
                "--source-type",
                "external",
                "--generation-path",
                "installed-quickstart",
                "--harness-label",
                "next pilot harness",
                "--out",
                "/tmp/NEXT_PILOT_PACK.md",
                "--issue-out",
                "/tmp/NEXT_ISSUE.md",
                "--min-successes",
                "2",
                "--min-score",
                "95",
                "--target-label",
                "tmp/next-pilot",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--generated-date",
                "2026-06-04",
                "--created",
                "2026-06-04T12:00:00Z",
                "--generated",
                "2026-06-04T12:00:00Z",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--pilot-status",
                "invited",
                "--pilot-notes",
                "sent to reporter",
                "--force",
                "--json",
            ],
            command,
        )

    def test_pilot_board_delegates_to_board_reporter(self):
        command, _ = self.run_cli(
            [
                "pilot-board",
                "--record-dir",
                "/tmp/pilot-records",
                "--usage-record-dir",
                "/tmp/usage-records",
                "--report",
                "/tmp/PILOT_BOARD.md",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/pilot_board.py",
                "--record-dir",
                "/tmp/pilot-records",
                "--usage-record-dir",
                "/tmp/usage-records",
                "--report",
                "/tmp/PILOT_BOARD.md",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_pilot_update_delegates_to_board_updater(self):
        command, _ = self.run_cli(
            [
                "pilot-update",
                "llm-app-pilot",
                "--status",
                "converted",
                "--record-dir",
                "/tmp/pilot-records",
                "--usage-record-dir",
                "/tmp/usage-records",
                "--report",
                "/tmp/PILOT_BOARD.md",
                "--notes",
                "converted after issue review",
                "--usage-record",
                "Docs/Environment/usage-records/llm-app-pilot.json",
                "--updated",
                "2026-06-04T14:00:00Z",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/pilot_board.py",
                "--update",
                "llm-app-pilot",
                "--status",
                "converted",
                "--record-dir",
                "/tmp/pilot-records",
                "--usage-record-dir",
                "/tmp/usage-records",
                "--report",
                "/tmp/PILOT_BOARD.md",
                "--notes",
                "converted after issue review",
                "--usage-record",
                "Docs/Environment/usage-records/llm-app-pilot.json",
                "--updated",
                "2026-06-04T14:00:00Z",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_beta_exit_audit_delegates_to_auditor(self):
        command, _ = self.run_cli(
            [
                "beta-exit-audit",
                "--record-dir",
                "/tmp/usage-records",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--usage-record-dir",
                "/tmp/usage-records",
                "--report",
                "/tmp/BETA_EXIT_AUDIT.md",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/beta_exit_audit.py",
                "--record-dir",
                "/tmp/usage-records",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--usage-record-dir",
                "/tmp/usage-records",
                "--report",
                "/tmp/BETA_EXIT_AUDIT.md",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_adoption_plan_delegates_to_planner(self):
        command, _ = self.run_cli(
            [
                "adoption-plan",
                "/tmp/source",
                "--profile",
                "software-development",
                "--project-name",
                "Source Project",
                "--blueprint-out",
                "/tmp/blueprint",
                "--force-blueprint",
                "--max-files",
                "25",
                "--limit",
                "2",
                "--source-label",
                "public source",
                "--report",
                "/tmp/ADOPTION_PLAN.md",
                "--copy-script",
                "/tmp/copy-adds.sh",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/plan_project_adoption.py",
                "/tmp/source",
                "--profile",
                "software-development",
                "--project-name",
                "Source Project",
                "--blueprint-out",
                "/tmp/blueprint",
                "--force-blueprint",
                "--max-files",
                "25",
                "--limit",
                "2",
                "--source-label",
                "public source",
                "--report",
                "/tmp/ADOPTION_PLAN.md",
                "--copy-script",
                "/tmp/copy-adds.sh",
                "--json",
            ],
            command,
        )

    def test_evidence_packet_delegates_to_exporter(self):
        command, _ = self.run_cli(
            [
                "evidence-packet",
                "/tmp/harness",
                "--out",
                "/tmp/HARNESS_EVIDENCE_PACKET.md",
                "--harness-label",
                "public harness label",
                "--min-successes",
                "1",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/export_evidence_packet.py",
                "/tmp/harness",
                "--out",
                "/tmp/HARNESS_EVIDENCE_PACKET.md",
                "--harness-label",
                "public harness label",
                "--min-successes",
                "1",
                "--json",
            ],
            command,
        )

    def test_pilot_pack_delegates_to_exporter(self):
        command, _ = self.run_cli(
            [
                "pilot-pack",
                "/tmp/harness",
                "--out",
                "/tmp/EXTERNAL_PILOT_PACK.md",
                "--issue-out",
                "/tmp/EXTERNAL_USAGE_ISSUE_DRAFT.md",
                "--harness-label",
                "public harness label",
                "--domain",
                "software development",
                "--slug",
                "external-pilot",
                "--title",
                "External pilot",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--min-successes",
                "2",
                "--prefill-from-trials",
                "--generated",
                "2026-06-04T12:00:00Z",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/export_pilot_pack.py",
                "/tmp/harness",
                "--domain",
                "software development",
                "--slug",
                "external-pilot",
                "--title",
                "External pilot",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--out",
                "/tmp/EXTERNAL_PILOT_PACK.md",
                "--issue-out",
                "/tmp/EXTERNAL_USAGE_ISSUE_DRAFT.md",
                "--harness-label",
                "public harness label",
                "--min-successes",
                "2",
                "--prefill-from-trials",
                "--generated",
                "2026-06-04T12:00:00Z",
                "--json",
            ],
            command,
        )

    def test_profiles_details_delegates_to_profile_catalog(self):
        command, _ = self.run_cli(["profiles", "--details"])

        self.assertEqual(["/usr/bin/python3", "scripts/profile_catalog.py"], command)

    def test_profiles_json_delegates_to_profile_catalog(self):
        command, _ = self.run_cli(["profiles", "--json"])

        self.assertEqual(["/usr/bin/python3", "scripts/profile_catalog.py", "--json"], command)

    def test_profile_delegates_to_profile_catalog(self):
        command, _ = self.run_cli(["profile", "security-audit", "--json"])

        self.assertEqual(
            ["/usr/bin/python3", "scripts/profile_catalog.py", "--profile", "security-audit", "--json"],
            command,
        )

    def test_recommend_delegates_to_profile_catalog(self):
        command, _ = self.run_cli(["recommend", "RAG app with evals", "--limit", "2", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/profile_catalog.py",
                "--recommend",
                "RAG app with evals",
                "--limit",
                "2",
                "--json",
            ],
            command,
        )

    def test_refresh_examples_delegates_to_refresh_script(self):
        command, _ = self.run_cli(
            [
                "refresh-examples",
                "--surface",
                "fixtures",
                "--fixture-root",
                "/tmp/fixtures",
                "--generated-date",
                "2026-06-04",
                "--created",
                "2026-06-04T12:00:00Z",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/refresh_generated_surfaces.py",
                "--surface",
                "fixtures",
                "--fixture-root",
                "/tmp/fixtures",
                "--generated-date",
                "2026-06-04",
                "--created",
                "2026-06-04T12:00:00Z",
                "--json",
            ],
            command,
        )

    def test_inspect_delegates_to_project_inspector(self):
        command, _ = self.run_cli(["inspect", "/tmp/project", "--max-files", "25", "--limit", "2", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/inspect_project.py",
                "/tmp/project",
                "--max-files",
                "25",
                "--limit",
                "2",
                "--json",
            ],
            command,
        )

    def test_generate_delegates_with_project_options(self):
        command, _ = self.run_cli(
            [
                "generate",
                "/tmp/example",
                "--profile",
                "knowledge-work",
                "--project-name",
                "Research Hub",
                "--force",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/generate_minimal_harness.py",
                "/tmp/example",
                "--profile",
                "knowledge-work",
                "--project-name",
                "Research Hub",
                "--force",
            ],
            command,
        )

    def test_acceptance_delegates_to_create_acceptance(self):
        command, _ = self.run_cli(
            [
                "acceptance",
                "/tmp/example",
                "--profile",
                "data-analysis",
                "--project-type",
                "CSV analysis",
                "--notes",
                "trial",
                "--force",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_create_acceptance.py",
                "/tmp/example",
                "--profile",
                "data-analysis",
                "--project-type",
                "CSV analysis",
                "--notes",
                "trial",
                "--force",
            ],
            command,
        )

    def test_brief_acceptance_delegates_to_brief_acceptance_script(self):
        command, _ = self.run_cli(
            [
                "brief-acceptance",
                "/tmp/example",
                "--brief",
                "RAG app with evals",
                "--project-name",
                "RAG Harness",
                "--notes",
                "trial",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "examples/brief",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_brief_acceptance.py",
                "/tmp/example",
                "--brief",
                "RAG app with evals",
                "--project-name",
                "RAG Harness",
                "--notes",
                "trial",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "examples/brief",
                "--force",
                "--json",
            ],
            command,
        )

    def test_demo_capture_delegates_to_demo_capture_script(self):
        command, _ = self.run_cli(
            [
                "demo-capture",
                "/tmp/example",
                "--brief",
                "RAG app with evals",
                "--project-name",
                "RAG Harness",
                "--notes",
                "demo",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "examples/demo",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_demo_capture.py",
                "/tmp/example",
                "--brief",
                "RAG app with evals",
                "--project-name",
                "RAG Harness",
                "--notes",
                "demo",
                "--limit",
                "2",
                "--allow-low-confidence",
                "--target-label",
                "examples/demo",
                "--force",
                "--json",
            ],
            command,
        )

    def test_gate_can_include_live_profile(self):
        command, _ = self.run_cli(["gate", "--codex-live", "--codex-live-profile", "all"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/run_evals.py",
                "--codex-live",
                "--codex-live-profile",
                "all",
            ],
            command,
        )

    def test_smoke_passes_live_prompt_after_paths(self):
        command, _ = self.run_cli(["smoke", "/tmp/example", "--codex-live", "--prompt", "Reply OK"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/smoke_generated_harness.py",
                "/tmp/example",
                "--codex-live",
                "--prompt",
                "Reply OK",
            ],
            command,
        )

    def test_validate_delegates_to_combined_validator(self):
        command, _ = self.run_cli(
            [
                "validate",
                "/tmp/example",
                "--min-score",
                "95",
                "--codex-live",
                "--prompt",
                "Reply OK",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/validate_generated_harness.py",
                "/tmp/example",
                "--min-score",
                "95",
                "--codex-live",
                "--prompt",
                "Reply OK",
                "--json",
            ],
            command,
        )

    def test_local_eval_delegates_to_generated_harness_eval_runner(self):
        command, _ = self.run_cli(
            [
                "local-eval",
                "/tmp/example",
                "--min-successes",
                "2",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "/tmp/example/scripts/run-harness-evals.py",
                "--min-successes",
                "2",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_migration_audit_delegates_to_migration_audit_script(self):
        command, _ = self.run_cli(
            [
                "migration-audit",
                "/tmp/example",
                "--report",
                "/tmp/CODEX_MIGRATION_PLAN.md",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/migration_audit.py",
                "/tmp/example",
                "--report",
                "/tmp/CODEX_MIGRATION_PLAN.md",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_semantic_alignment_delegates_to_checker(self):
        command, _ = self.run_cli(["semantic-alignment", "--timeout", "5", "--no-write", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/check_semantic_alignment.py",
                "--timeout",
                "5",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_source_freshness_passes_no_write_and_json(self):
        command, _ = self.run_cli(["source-freshness", "--timeout", "5", "--no-write", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/check_source_freshness.py",
                "--timeout",
                "5",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_proof_status_passes_beta_exit_flag(self):
        command, _ = self.run_cli(["proof-status", "--beta-exit", "--no-write", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/proof_status.py",
                "--beta-exit",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_equivalence_delegates_to_checker(self):
        command, _ = self.run_cli(["equivalence", "--report", "/tmp/CODEX_EQUIVALENCE_MATRIX.md", "--no-write", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/check_codex_equivalence.py",
                "--report",
                "/tmp/CODEX_EQUIVALENCE_MATRIX.md",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_equivalence_uses_current_checkout_when_available(self):
        parser = codex_harness.make_parser()
        args = parser.parse_args(["equivalence"])

        self.assertEqual(Path.cwd(), codex_harness.command_cwd(args))

    def test_usage_record_delegates_to_recorder(self):
        command, _ = self.run_cli(
            [
                "usage-record",
                "--slug",
                "demo",
                "--title",
                "Demo",
                "--domain",
                "software",
                "--harness-path",
                "examples/demo",
                "--task-summary",
                "Public-safe task.",
                "--outcome",
                "success",
                "--evidence-type",
                "synthetic",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--evidence",
                "report written",
                "--verification",
                "tests passed",
                "--privacy-review",
                "Synthetic only.",
                "--limitation",
                "One task.",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_RECORDS.md",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/record_usage_case.py",
                "--slug",
                "demo",
                "--title",
                "Demo",
                "--domain",
                "software",
                "--harness-path",
                "examples/demo",
                "--task-summary",
                "Public-safe task.",
                "--outcome",
                "success",
                "--evidence-type",
                "synthetic",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--privacy-review",
                "Synthetic only.",
                "--evidence",
                "report written",
                "--verification",
                "tests passed",
                "--limitation",
                "One task.",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_RECORDS.md",
                "--force",
                "--json",
            ],
            command,
        )

    def test_usage_from_harness_delegates_to_bridge_script(self):
        command, _ = self.run_cli(
            [
                "usage-from-harness",
                "/tmp/harness",
                "--slug",
                "demo",
                "--title",
                "Demo",
                "--domain",
                "software",
                "--harness-label",
                "public harness label",
                "--task-summary",
                "Public-safe task.",
                "--outcome",
                "success",
                "--evidence-type",
                "synthetic",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--evidence",
                "extra evidence",
                "--verification",
                "extra verification",
                "--privacy-review",
                "Synthetic only.",
                "--limitation",
                "One task.",
                "--generated",
                "2026-06-04T00:00:00Z",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_RECORDS.md",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--pilot-board-report",
                "/tmp/PILOT_BOARD.md",
                "--pilot-notes",
                "converted from harness report",
                "--force",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/usage_from_harness.py",
                "/tmp/harness",
                "--slug",
                "demo",
                "--title",
                "Demo",
                "--domain",
                "software",
                "--evidence-type",
                "synthetic",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--privacy-review",
                "Synthetic only.",
                "--harness-label",
                "public harness label",
                "--task-summary",
                "Public-safe task.",
                "--outcome",
                "success",
                "--evidence",
                "extra evidence",
                "--verification",
                "extra verification",
                "--limitation",
                "One task.",
                "--generated",
                "2026-06-04T00:00:00Z",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_RECORDS.md",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--pilot-board-report",
                "/tmp/PILOT_BOARD.md",
                "--pilot-notes",
                "converted from harness report",
                "--force",
                "--json",
            ],
            command,
        )

    def test_usage_from_issue_delegates_to_issue_importer_script(self):
        command, _ = self.run_cli(
            [
                "usage-from-issue",
                "/tmp/issue.md",
                "--slug",
                "external-demo",
                "--title",
                "External demo",
                "--harness-label",
                "public harness label",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--generated",
                "2026-06-04T00:00:00Z",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_RECORDS.md",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--pilot-board-report",
                "/tmp/PILOT_BOARD.md",
                "--pilot-notes",
                "converted from issue",
                "--force",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/usage_from_issue.py",
                "/tmp/issue.md",
                "--slug",
                "external-demo",
                "--title",
                "External demo",
                "--harness-label",
                "public harness label",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--generated",
                "2026-06-04T00:00:00Z",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_RECORDS.md",
                "--pilot-record-dir",
                "/tmp/pilot-records",
                "--pilot-board-report",
                "/tmp/PILOT_BOARD.md",
                "--pilot-notes",
                "converted from issue",
                "--force",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_pilot_campaign_delegates_to_campaign_script(self):
        command, _ = self.run_cli(
            [
                "pilot-campaign",
                "--record-dir",
                "/tmp/records",
                "--out",
                "/tmp/PILOT_CAMPAIGN.md",
                "--max-pilots",
                "2",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/export_pilot_campaign.py",
                "--record-dir",
                "/tmp/records",
                "--out",
                "/tmp/PILOT_CAMPAIGN.md",
                "--max-pilots",
                "2",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_usage_validate_delegates_to_validator(self):
        command, _ = self.run_cli(
            [
                "usage-validate",
                "--record-dir",
                "/tmp/records",
                "--min-records",
                "1",
                "--require-non-synthetic",
                "--require-success",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/validate_usage_records.py",
                "--record-dir",
                "/tmp/records",
                "--min-records",
                "1",
                "--require-non-synthetic",
                "--require-success",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--json",
            ],
            command,
        )

    def test_usage_gaps_delegates_to_gap_report(self):
        command, _ = self.run_cli(
            [
                "usage-gaps",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_GAPS.md",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/usage_gaps.py",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/USAGE_GAPS.md",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_proof_next_delegates_to_next_action_report(self):
        command, _ = self.run_cli(
            [
                "proof-next",
                "/tmp/next-pilot",
                "--record-dir",
                "/tmp/records",
                "--pilot-record-dir",
                "/tmp/pilots",
                "--pilot-board-report",
                "/tmp/PILOT_BOARD.md",
                "--usage-report",
                "/tmp/USAGE_RECORDS.md",
                "--pilot-pack-out",
                "/tmp/NEXT_PACK.md",
                "--issue-out",
                "/tmp/NEXT_ISSUE.md",
                "--report",
                "/tmp/PROOF_NEXT.md",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/proof_next.py",
                "/tmp/next-pilot",
                "--record-dir",
                "/tmp/records",
                "--pilot-record-dir",
                "/tmp/pilots",
                "--pilot-board-report",
                "/tmp/PILOT_BOARD.md",
                "--usage-report",
                "/tmp/USAGE_RECORDS.md",
                "--pilot-pack-out",
                "/tmp/NEXT_PACK.md",
                "--issue-out",
                "/tmp/NEXT_ISSUE.md",
                "--report",
                "/tmp/PROOF_NEXT.md",
                "--min-records",
                "5",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_proof_status_delegates_to_status_script(self):
        command, _ = self.run_cli(
            [
                "proof-status",
                "--min-live-trials",
                "8",
                "--min-usage-records",
                "1",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/PROOF_STATUS.md",
                "--no-write",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/proof_status.py",
                "--min-live-trials",
                "8",
                "--min-usage-records",
                "1",
                "--min-external-or-multi-project",
                "3",
                "--min-domains",
                "4",
                "--min-installed-init-brief",
                "2",
                "--record-dir",
                "/tmp/records",
                "--report",
                "/tmp/PROOF_STATUS.md",
                "--no-write",
                "--json",
            ],
            command,
        )

    def test_doctor_delegates_to_doctor_script(self):
        command, _ = self.run_cli(
            [
                "doctor",
                "--record-dir",
                "/tmp/records",
                "--min-usage-records",
                "5",
                "--include-install-smoke",
                "--json",
            ]
        )

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/doctor.py",
                "--record-dir",
                "/tmp/records",
                "--min-usage-records",
                "5",
                "--include-install-smoke",
                "--json",
            ],
            command,
        )


if __name__ == "__main__":
    unittest.main()

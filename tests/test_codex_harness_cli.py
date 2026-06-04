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
        command, _ = self.run_cli(["migration-audit", "/tmp/example", "--json"])

        self.assertEqual(
            [
                "/usr/bin/python3",
                "scripts/migration_audit.py",
                "/tmp/example",
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
                "--force",
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

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


if __name__ == "__main__":
    unittest.main()

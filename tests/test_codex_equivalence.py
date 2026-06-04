import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_codex_equivalence.py"

spec = importlib.util.spec_from_file_location("check_codex_equivalence", SCRIPT)
check_codex_equivalence = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(check_codex_equivalence)


class CodexEquivalenceTests(unittest.TestCase):
    def test_current_repo_passes_equivalence_matrix(self):
        payload = check_codex_equivalence.build_payload()

        self.assertEqual("pass", payload["status"], payload["failures"])
        self.assertGreaterEqual(payload["capability_count"], 10)
        names = {capability["name"] for capability in payload["capabilities"]}
        self.assertIn("Generation", names)
        self.assertIn("Usage evidence", names)
        self.assertIn("Release proof", names)

    def test_missing_evidence_path_fails_capability(self):
        original = check_codex_equivalence.CAPABILITIES
        check_codex_equivalence.CAPABILITIES = [
            {
                "name": "Missing thing",
                "original_need": "A missing thing.",
                "codex_surface": "No surface.",
                "evidence_paths": ["not-here.md"],
                "commands": [],
            }
        ]
        try:
            payload = check_codex_equivalence.build_payload()
        finally:
            check_codex_equivalence.CAPABILITIES = original

        self.assertEqual("fail", payload["status"])
        self.assertEqual(["not-here.md"], payload["failures"][0]["missing_paths"])

    def test_missing_cli_command_fails_capability(self):
        original = check_codex_equivalence.CAPABILITIES
        check_codex_equivalence.CAPABILITIES = [
            {
                "name": "Missing command",
                "original_need": "A missing command.",
                "codex_surface": "No command.",
                "evidence_paths": ["README.md"],
                "commands": ["codex-harness not-a-command"],
            }
        ]
        try:
            payload = check_codex_equivalence.build_payload()
        finally:
            check_codex_equivalence.CAPABILITIES = original

        self.assertEqual("fail", payload["status"])
        self.assertEqual(["not-a-command"], payload["failures"][0]["missing_commands"])

    def test_write_report_includes_claim_boundary(self):
        payload = {
            "generated": "2026-06-04T12:00:00Z",
            "status": "pass",
            "capability_count": 1,
            "failure_count": 0,
            "failures": [],
            "capabilities": [
                {
                    "name": "Generation",
                    "status": "pass",
                    "original_need": "Create a ready-to-use harness directory.",
                    "codex_surface": "codex-harness init.",
                    "evidence_paths": ["scripts/generate_minimal_harness.py"],
                    "commands": ["codex-harness init <target>"],
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "CODEX_EQUIVALENCE_MATRIX.md"
            check_codex_equivalence.write_report(report, payload)
            text = report.read_text(encoding="utf-8")

        self.assertIn("# Codex Equivalence Matrix", text)
        self.assertIn("not external adoption", text)
        self.assertIn("| Generation | PASS |", text)


if __name__ == "__main__":
    unittest.main()

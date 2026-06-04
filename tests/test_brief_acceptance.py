import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BriefAcceptanceTests(unittest.TestCase):
    def run_brief_acceptance(self, target: Path, *extra: str) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_brief_acceptance.py",
                target.as_posix(),
                "--json",
                *extra,
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_brief_acceptance_selects_profile_and_records_selection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "accepted"
            payload = self.run_brief_acceptance(
                target,
                "--brief",
                "RAG app with prompts, evals, retrieval quality checks, and tool calls.",
                "--project-name",
                "RAG Quality Harness",
                "--target-label",
                "examples/brief-acceptance/rag-quality",
            )

            self.assertEqual("pass", payload["status"])
            self.assertEqual("llm-app", payload["profile"])
            self.assertEqual("pass", payload["eval"]["status"])
            self.assertEqual("pass", payload["smoke"]["status"])
            self.assertTrue((target / "Docs/Environment/PROFILE_SELECTION.md").is_file())
            manifest = (target / "Docs/Environment/MANIFEST.md").read_text(encoding="utf-8")
            selection = (target / "Docs/Environment/PROFILE_SELECTION.md").read_text(encoding="utf-8")
            self.assertIn("- Docs/Environment/PROFILE_SELECTION.md", manifest)
            self.assertIn("- Profile: llm-app", selection)
            self.assertIn("- Confidence: high", selection)
            self.assertIn("RAG app with prompts", selection)

    def test_brief_acceptance_rejects_low_confidence_without_override(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "accepted"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_brief_acceptance.py",
                    target.as_posix(),
                    "--brief",
                    "zzqx plorn mivv",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(0, completed.returncode)
            self.assertIn("No confident deterministic profile match", completed.stderr)


if __name__ == "__main__":
    unittest.main()

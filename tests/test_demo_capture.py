import tempfile
import unittest
from pathlib import Path

import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_demo_capture


class DemoCaptureTests(unittest.TestCase):
    def test_demo_capture_writes_report_and_validates_generated_harness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "demo"

            payload = run_demo_capture.run_demo_capture(
                target=target,
                brief="RAG app with prompts, evals, and retrieval checks",
                project_name="Demo Harness",
                notes="unit test demo capture",
                force=False,
                generated_date="2026-06-04",
                created="2026-06-04T00:00:00Z",
                limit=3,
                allow_low_confidence=False,
            )

            self.assertEqual("pass", payload["status"])
            self.assertEqual("llm-app", payload["profile"])
            report = target / "Docs" / "Environment" / "DEMO_CAPTURE.md"
            self.assertTrue(report.is_file())
            text = report.read_text(encoding="utf-8")
            self.assertIn("# Demo Capture", text)
            self.assertIn("PROFILE_SELECTION.md", text)
            self.assertIn("AGENTS.md", text)
            self.assertIn("Combined validation: pass", text)
            manifest = (target / "Docs" / "Environment" / "MANIFEST.md").read_text(encoding="utf-8")
            self.assertIn("Docs/Environment/DEMO_CAPTURE.md", manifest)


if __name__ == "__main__":
    unittest.main()

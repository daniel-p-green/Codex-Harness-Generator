import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
QUICKSTART_PATH = REPO_ROOT / "scripts" / "run_quickstart.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("run_quickstart", QUICKSTART_PATH)
run_quickstart = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_quickstart)


class QuickstartTests(unittest.TestCase):
    def test_quickstart_generates_validated_locally_evaluated_harness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "quick"
            args = type(
                "Args",
                (),
                {
                    "target": target.as_posix(),
                    "brief": "RAG app with prompts, evals, and retrieval checks",
                    "project_name": "Quickstart RAG Harness",
                    "notes": "quickstart test",
                    "force": False,
                    "generated_date": "2026-06-04",
                    "created": "2026-06-04T12:00:00Z",
                    "limit": 3,
                    "allow_low_confidence": False,
                    "target_label": None,
                    "min_score": 90,
                    "min_successes": 0,
                    "no_write": False,
                },
            )()

            payload = run_quickstart.build_payload(args)

            self.assertEqual("pass", payload["status"], payload)
            self.assertEqual("llm-app", payload["profile"])
            self.assertEqual("pass", payload["doctor"]["status"])
            self.assertEqual("pass", payload["init"]["status"])
            self.assertEqual("pass", payload["validate"]["status"])
            self.assertEqual("pass", payload["local_eval"]["status"])

            report = target / "Docs" / "Environment" / "QUICKSTART_REPORT.md"
            manifest = target / "Docs" / "Environment" / "MANIFEST.md"
            self.assertTrue(report.is_file())
            self.assertIn("not prove external adoption", report.read_text(encoding="utf-8"))
            self.assertIn("record-task-trial.py", report.read_text(encoding="utf-8"))
            self.assertIn("- Docs/Environment/QUICKSTART_REPORT.md", manifest.read_text(encoding="utf-8"))

    def test_low_confidence_brief_requires_explicit_override(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = type(
                "Args",
                (),
                {
                    "target": (Path(temp_dir) / "quick").as_posix(),
                    "brief": "xqzv jklm nrrp",
                    "project_name": "Unknown Harness",
                    "notes": "quickstart test",
                    "force": False,
                    "generated_date": "2026-06-04",
                    "created": "2026-06-04T12:00:00Z",
                    "limit": 3,
                    "allow_low_confidence": False,
                    "target_label": None,
                    "min_score": 90,
                    "min_successes": 0,
                    "no_write": False,
                },
            )()

            with self.assertRaises(SystemExit):
                run_quickstart.build_payload(args)


if __name__ == "__main__":
    unittest.main()

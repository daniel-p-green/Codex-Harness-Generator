import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_EVALS_PATH = REPO_ROOT / "scripts" / "run_evals.py"

spec = importlib.util.spec_from_file_location("run_evals", RUN_EVALS_PATH)
run_evals = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_evals)


class RunEvalsTests(unittest.TestCase):
    def test_create_acceptance_live_paths_default_profile(self):
        paths = run_evals.create_acceptance_live_paths("software-development")

        self.assertEqual(1, len(paths))
        self.assertTrue(paths[0].endswith("examples/create-acceptance/software-development"))

    def test_create_acceptance_live_paths_all_profiles(self):
        paths = run_evals.create_acceptance_live_paths("all")

        self.assertGreaterEqual(len(paths), 4)
        self.assertTrue(any(path.endswith("examples/create-acceptance/data-analysis") for path in paths))
        self.assertTrue(any(path.endswith("examples/create-acceptance/devops-infrastructure") for path in paths))
        self.assertTrue(any(path.endswith("examples/create-acceptance/knowledge-work") for path in paths))
        self.assertTrue(any(path.endswith("examples/create-acceptance/software-development") for path in paths))

    def test_create_acceptance_live_paths_missing_profile(self):
        self.assertEqual([], run_evals.create_acceptance_live_paths("missing-profile"))

    def test_live_create_example_paths_include_checked_in_captures(self):
        paths = run_evals.live_create_example_paths()

        self.assertGreaterEqual(len(paths), 3)
        self.assertTrue(any(path.endswith("examples/live-create/synthetic-markdown-notes") for path in paths))
        self.assertTrue(any(path.endswith("examples/live-create/synthetic-python-cli") for path in paths))
        self.assertTrue(any(path.endswith("examples/live-create/synthetic-data-review") for path in paths))

    def test_brief_acceptance_example_paths_include_checked_in_examples(self):
        paths = run_evals.brief_acceptance_example_paths()

        self.assertEqual(4, len(paths))
        self.assertTrue(any(path.endswith("examples/brief-acceptance/rag-quality") for path in paths))
        self.assertTrue(any(path.endswith("examples/brief-acceptance/security-review") for path in paths))

    def test_demo_capture_example_paths_include_checked_in_demo(self):
        paths = run_evals.demo_capture_example_paths()

        self.assertEqual(1, len(paths))
        self.assertTrue(paths[0].endswith("examples/demo-capture/rag-quality"))

    def test_run_step_fails_and_removes_added_usage_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "usage-records"
            record_dir.mkdir()
            writer = root / "write_record.py"
            writer.write_text(
                "from pathlib import Path\n"
                f"Path({str(record_dir / 'accidental.json')!r}).write_text('{{}}\\n', encoding='utf-8')\n",
                encoding="utf-8",
            )

            with patch.object(run_evals, "USAGE_RECORD_DIR", record_dir):
                result = run_evals.run_step("mutating_step", [sys.executable, writer.as_posix()])

        self.assertEqual("fail", result["status"])
        self.assertEqual(1, result["returncode"])
        self.assertIn("checked-in usage records changed", result["stderr"])
        self.assertIn("accidental.json", result["stderr"])
        self.assertFalse((record_dir / "accidental.json").exists())


if __name__ == "__main__":
    unittest.main()

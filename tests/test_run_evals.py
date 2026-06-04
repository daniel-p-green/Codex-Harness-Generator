import importlib.util
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()

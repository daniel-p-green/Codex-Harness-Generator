import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIEF_ACCEPTANCE_EXAMPLES = [
    "hiring-scorecard",
    "rag-quality",
    "security-review",
    "support-escalation",
]


class BriefAcceptanceExampleTests(unittest.TestCase):
    def test_refresh_brief_acceptance_examples_outputs_valid_harnesses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            example_root = Path(temp_dir) / "brief-acceptance"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/refresh_brief_acceptance_examples.py",
                    "--example-root",
                    example_root.as_posix(),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                raise AssertionError(completed.stdout + completed.stderr)

            self.assertTrue((example_root / "README.md").is_file())
            generated = sorted(path for path in example_root.iterdir() if path.is_dir())
            self.assertEqual(BRIEF_ACCEPTANCE_EXAMPLES, [path.name for path in generated])
            for target in generated:
                self.assertTrue((target / "Docs/Environment/CREATION_CONTEXT.md").is_file())
                self.assertTrue((target / "Docs/Environment/CREATE_ACCEPTANCE_REPORT.md").is_file())
                self.assertTrue((target / "Docs/Environment/PROFILE_SELECTION.md").is_file())

            eval_completed = subprocess.run(
                [sys.executable, "scripts/eval_generated_harness.py", *[target.as_posix() for target in generated]],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, eval_completed.returncode, eval_completed.stdout + eval_completed.stderr)


if __name__ == "__main__":
    unittest.main()

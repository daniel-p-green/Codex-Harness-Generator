import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CREATE_ACCEPTANCE_PROFILES = [
    "data-analysis",
    "devops-infrastructure",
    "knowledge-work",
    "software-development",
]


class CreateAcceptanceTests(unittest.TestCase):
    def run_acceptance(self, target: Path, *extra: str) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/run_create_acceptance.py",
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

    def test_create_acceptance_preserves_trigger_context_and_passes_eval(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "accepted"
            payload = self.run_acceptance(
                target,
                "--profile",
                "data-analysis",
                "--project-name",
                "Metric Review Workspace",
                "--project-type",
                "Data analysis",
                "--notes",
                "weekly metric review",
                "--target-label",
                "examples/create-acceptance/data-analysis",
            )

            self.assertEqual("pass", payload["status"])
            self.assertEqual("data-analysis", payload["profile"])
            self.assertEqual("pass", payload["eval"]["status"])
            self.assertEqual(100, payload["eval"]["score"])
            self.assertEqual("pass", payload["smoke"]["status"])

            context = target / "Docs/Environment/CREATION_CONTEXT.md"
            report = target / "Docs/Environment/CREATE_ACCEPTANCE_REPORT.md"
            manifest = (target / "Docs/Environment/MANIFEST.md").read_text(encoding="utf-8")
            self.assertTrue(context.is_file())
            self.assertTrue(report.is_file())
            self.assertIn("- Docs/Environment/CREATION_CONTEXT.md", manifest)
            self.assertIn("- Docs/Environment/CREATE_ACCEPTANCE_REPORT.md", manifest)
            self.assertIn(
                "- Path: examples/create-acceptance/data-analysis",
                context.read_text(encoding="utf-8"),
            )
            self.assertIn("Metric Review Workspace", (target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_refresh_create_acceptance_examples_outputs_valid_harnesses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            example_root = Path(temp_dir) / "create-acceptance"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/refresh_create_acceptance_examples.py",
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
            self.assertEqual(CREATE_ACCEPTANCE_PROFILES, [path.name for path in generated])
            for target in generated:
                self.assertTrue((target / "Docs/Environment/CREATION_CONTEXT.md").is_file())
                self.assertTrue((target / "Docs/Environment/CREATE_ACCEPTANCE_REPORT.md").is_file())

            eval_completed = subprocess.run(
                [sys.executable, "scripts/eval_generated_harness.py", *[target.as_posix() for target in generated]],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, eval_completed.returncode, eval_completed.stdout + eval_completed.stderr)

    def test_create_acceptance_rejects_non_empty_target_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "existing"
            target.mkdir()
            (target / "keep.txt").write_text("keep\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_create_acceptance.py",
                    target.as_posix(),
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(0, completed.returncode)
            self.assertIn("Target is not empty", completed.stderr)


if __name__ == "__main__":
    unittest.main()

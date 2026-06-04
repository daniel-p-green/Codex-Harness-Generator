import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class InspectedAcceptanceTests(unittest.TestCase):
    def make_source_project(self, root: Path) -> Path:
        source = root / "rag-source"
        (source / "src").mkdir(parents=True)
        (source / "prompts").mkdir()
        (source / "data").mkdir()
        (source / "pyproject.toml").write_text("[project]\nname = \"rag-source\"\n", encoding="utf-8")
        (source / "src" / "retrieval.py").write_text("def search():\n    return []\n", encoding="utf-8")
        (source / "prompts" / "answer.md").write_text("Answer with sources.\n", encoding="utf-8")
        (source / "data" / "evals.csv").write_text("query,expected\n", encoding="utf-8")
        return source

    def test_inspected_acceptance_generates_harness_and_records_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = self.make_source_project(root)
            target = root / "generated"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_inspected_acceptance.py",
                    target.as_posix(),
                    "--from-project",
                    source.as_posix(),
                    "--source-label",
                    "public-safe-rag-source",
                    "--target-label",
                    "tmp/generated",
                    "--force",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertEqual("llm-app", payload["profile"])
            self.assertEqual("public-safe-rag-source", payload["source_label"])
            self.assertTrue((target / "Docs/Environment/PROJECT_INSPECTION.md").is_file())
            report = (target / "Docs/Environment/PROJECT_INSPECTION.md").read_text(encoding="utf-8")
            selection = (target / "Docs/Environment/PROFILE_SELECTION.md").read_text(encoding="utf-8")
            manifest = (target / "Docs/Environment/MANIFEST.md").read_text(encoding="utf-8")
            self.assertIn("Source label: public-safe-rag-source", report)
            self.assertIn("Privacy Boundary", report)
            self.assertIn("Flow: metadata-inspected deterministic acceptance.", selection)
            self.assertIn("- Docs/Environment/PROJECT_INSPECTION.md", manifest)


if __name__ == "__main__":
    unittest.main()

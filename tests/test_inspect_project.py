import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "inspect_project.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("inspect_project", SCRIPT)
inspect_project = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = inspect_project
spec.loader.exec_module(inspect_project)


class InspectProjectTests(unittest.TestCase):
    def make_project(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name) / "rag-app"
        (root / "src").mkdir(parents=True)
        (root / "tests").mkdir()
        (root / "prompts").mkdir()
        (root / "data").mkdir()
        (root / ".git").mkdir()
        (root / "pyproject.toml").write_text("[project]\nname = \"rag-app\"\n", encoding="utf-8")
        (root / "README.md").write_text("# RAG app\n", encoding="utf-8")
        (root / "src" / "retrieval.py").write_text("def search():\n    return []\n", encoding="utf-8")
        (root / "tests" / "test_retrieval.py").write_text("def test_search():\n    assert True\n", encoding="utf-8")
        (root / "prompts" / "answer.md").write_text("Use sources.\n", encoding="utf-8")
        (root / "data" / "evals.csv").write_text("query,expected\n", encoding="utf-8")
        (root / ".git" / "ignored.py").write_text("ignored\n", encoding="utf-8")
        return temp_dir, root

    def test_build_payload_recommends_from_project_signals_without_absolute_paths(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        payload = inspect_project.build_payload(root, max_files=100, limit=3)

        self.assertEqual("pass", payload["status"])
        self.assertEqual("rag-app", payload["project"])
        self.assertEqual("llm-app", payload["recommended_profile"])
        self.assertIn("pyproject.toml", payload["signals"]["config_files"])
        self.assertIn("prompts", payload["signals"]["directories"])
        self.assertIn(".py", payload["signals"]["extensions"])
        self.assertTrue(all(temp_dir.name not in item for item in payload["signals"]["sample_files"]))
        self.assertNotIn(temp_dir.name, json.dumps(payload))

    def test_inspect_project_cli_emits_json(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        completed = subprocess.run(
            [sys.executable, SCRIPT.as_posix(), root.as_posix(), "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("llm-app", payload["recommended_profile"])
        self.assertIn("codex-harness init <target>", payload["next_command"])

    def test_inspect_project_rejects_missing_path(self):
        completed = subprocess.run(
            [sys.executable, SCRIPT.as_posix(), "/definitely/not/a/project", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("does not exist", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()

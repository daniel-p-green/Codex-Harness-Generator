import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "plan_project_adoption.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("plan_project_adoption", SCRIPT)
plan_project_adoption = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = plan_project_adoption
spec.loader.exec_module(plan_project_adoption)


class PlanProjectAdoptionTests(unittest.TestCase):
    def make_project(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name) / "rag-app"
        (root / "src").mkdir(parents=True)
        (root / "prompts").mkdir()
        (root / "tests").mkdir()
        (root / "AGENTS.md").write_text("# Existing Instructions\n\nKeep this project-specific guidance.\n", encoding="utf-8")
        (root / "pyproject.toml").write_text("[project]\nname = \"rag-app\"\n", encoding="utf-8")
        (root / "src" / "retrieval.py").write_text("def search():\n    return []\n", encoding="utf-8")
        (root / "prompts" / "answer.md").write_text("Use sources.\n", encoding="utf-8")
        (root / "tests" / "test_retrieval.py").write_text("def test_search():\n    assert True\n", encoding="utf-8")
        return temp_dir, root

    def test_build_payload_detects_adds_and_conflicts_without_absolute_paths(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        payload = plan_project_adoption.build_payload(
            project=root,
            profile=None,
            project_name=None,
            harness=None,
            blueprint_out=None,
            force_blueprint=False,
            max_files=100,
            limit=3,
            generated_date="2026-06-04",
            source_label="public rag app",
        )

        self.assertEqual("pass", payload["status"])
        self.assertEqual("public rag app", payload["project"])
        self.assertEqual("llm-app", payload["profile"])
        self.assertGreater(payload["summary"]["add"], 0)
        self.assertGreaterEqual(payload["summary"]["conflict"], 1)
        self.assertTrue(any(item["path"] == "AGENTS.md" for item in payload["conflicts"]))
        self.assertTrue(any(check["command"] == "python scripts/check-harness.py" for check in payload["post_adoption_checks"]))
        self.assertNotIn(temp_dir.name, json.dumps(payload))

    def test_write_report_lists_conflicts_and_privacy_boundary(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        payload = plan_project_adoption.build_payload(
            project=root,
            profile="software-development",
            project_name="RAG App",
            harness=None,
            blueprint_out=None,
            force_blueprint=False,
            max_files=100,
            limit=3,
            generated_date="2026-06-04",
            source_label=None,
        )
        report = Path(temp_dir.name) / "ADOPTION_PLAN.md"
        plan_project_adoption.write_report(report, payload)

        text = report.read_text(encoding="utf-8")
        self.assertIn("# Harness Adoption Plan", text)
        self.assertIn("## Post-Adoption Checks", text)
        self.assertIn("`python scripts/check-harness.py`", text)
        self.assertIn("`AGENTS.md` | conflict", text)
        self.assertIn("It does not include source file contents", text)

    def test_blueprint_out_and_copy_script_copy_only_add_rows(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)
        original_agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        blueprint = Path(temp_dir.name) / "blueprint"
        copy_script = Path(temp_dir.name) / "copy-adds.sh"

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                root.as_posix(),
                "--source-label",
                "public rag app",
                "--blueprint-out",
                blueprint.as_posix(),
                "--copy-script",
                copy_script.as_posix(),
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
        self.assertEqual(copy_script.as_posix(), payload["copy_script"])
        self.assertTrue((blueprint / "AGENTS.md").exists())
        self.assertTrue(copy_script.exists())
        self.assertTrue(copy_script.stat().st_mode & 0o111)
        script_text = copy_script.read_text(encoding="utf-8")
        self.assertIn("Refusing to overwrite existing path", script_text)
        self.assertIn("Next checks:", script_text)
        self.assertIn("python scripts/run-harness-evals.py --no-write", script_text)
        self.assertNotIn("cp \"$BLUEPRINT_DIR\"/AGENTS.md", script_text)

        copy_completed = subprocess.run(
            [copy_script.as_posix()],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, copy_completed.returncode, copy_completed.stdout + copy_completed.stderr)
        self.assertEqual(original_agents, (root / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertTrue((root / ".codex" / "config.toml").exists())
        self.assertTrue((root / "scripts" / "check-harness.py").exists())

    def test_copy_script_requires_persistent_blueprint(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                root.as_posix(),
                "--copy-script",
                str(Path(temp_dir.name) / "copy-adds.sh"),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("--copy-script requires --harness or --blueprint-out", completed.stderr + completed.stdout)

    def test_cli_emits_json(self):
        temp_dir, root = self.make_project()
        self.addCleanup(temp_dir.cleanup)

        completed = subprocess.run(
            [sys.executable, SCRIPT.as_posix(), root.as_posix(), "--source-label", "public rag app", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("llm-app", payload["profile"])
        self.assertGreater(payload["summary"]["add"], 0)
        self.assertIn("post_adoption_checks", payload)

    def test_rejects_missing_project(self):
        completed = subprocess.run(
            [sys.executable, SCRIPT.as_posix(), "/definitely/not/a/project"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("does not exist", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()

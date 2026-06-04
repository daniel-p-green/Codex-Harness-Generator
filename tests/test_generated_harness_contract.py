import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = REPO_ROOT / "scripts" / "eval_generated_harness.py"
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses"

spec = importlib.util.spec_from_file_location("eval_generated_harness", EVAL_PATH)
eval_generated_harness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = eval_generated_harness
spec.loader.exec_module(eval_generated_harness)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class GeneratedHarnessContractTests(unittest.TestCase):
    def fixture_paths(self) -> list[Path]:
        return sorted(path for path in FIXTURES_ROOT.iterdir() if path.is_dir())

    def copy_fixture(self, name: str = "software-dev-basic") -> tuple[tempfile.TemporaryDirectory, Path]:
        temp_dir = tempfile.TemporaryDirectory()
        target = Path(temp_dir.name) / name
        shutil.copytree(FIXTURES_ROOT / name, target)
        return temp_dir, target

    def assert_has_check(self, result: dict, check: str) -> None:
        checks = {finding["check"] for finding in result["findings"]}
        self.assertIn(check, checks, result)

    def test_all_generated_harness_fixtures_pass_with_high_scores(self):
        fixtures = self.fixture_paths()
        self.assertGreaterEqual(len(fixtures), 5)
        for fixture in fixtures:
            with self.subTest(fixture=fixture.name):
                result = eval_generated_harness.evaluate(fixture)
                self.assertEqual("pass", result["status"], result)
                self.assertGreaterEqual(result["score"], 90, result)
                self.assertEqual(0, result["failure_count"], result)

    def test_cli_accepts_all_generated_harness_fixtures(self):
        command = [
            sys.executable,
            "scripts/eval_generated_harness.py",
            "--json",
            *[path.as_posix() for path in self.fixture_paths()],
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn('"status": "pass"', completed.stdout)

    def test_smoke_cli_accepts_all_generated_harness_fixtures(self):
        command = [
            sys.executable,
            "scripts/smoke_generated_harness.py",
            "--json",
            *[path.as_posix() for path in self.fixture_paths()],
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn('"status": "pass"', completed.stdout)

    def test_smoke_cli_catches_missing_skill_file(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        (target / ".agents/skills/health-check/SKILL.md").unlink()

        command = [
            sys.executable,
            "scripts/smoke_generated_harness.py",
            "--json",
            target.as_posix(),
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn('"status": "fail"', completed.stdout)

    def test_missing_required_docs_fail(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        (target / "Docs/Environment/VALIDATION_REPORT.md").unlink()

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "required_path")

    def test_broken_skills_config_target_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("../.agents/skills/health-check", "../.agents/skills/missing"),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "skills_config")

    def test_missing_skill_metadata_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(target / ".agents/skills/health-check/SKILL.md", "# Health Check\n")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "skill_metadata")

    def test_agent_registry_target_missing_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace('config_file = "agents/reviewer.toml"', 'config_file = "agents/missing.toml"'),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "agent_registry")

    def test_agent_name_mismatch_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        agent = target / ".codex/agents/reviewer.toml"
        agent.write_text(
            agent.read_text(encoding="utf-8").replace('name = "reviewer"', 'name = "wrong-reviewer"'),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "agent_schema")

    def test_permission_profile_without_glob_depth_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("[permissions.software-dev.filesystem]\nglob_scan_max_depth = 4\n\n", ""),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "permission_globs")

    def test_hooks_flag_without_hook_config_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("[agents]\n", "[features]\nhooks = true\n\n[agents]\n"),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "hooks_config")

    def test_legacy_runtime_path_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(target / ".claude/settings.json", "{}\n")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "forbidden_path")

    def test_missing_source_map_citation_warns_and_lowers_score(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        source_map = target / "Docs/Environment/SOURCE_MAP.md"
        source_map.write_text(
            source_map.read_text(encoding="utf-8").replace("- https://developers.openai.com/codex/skills\n", ""),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("pass", result["status"], result)
        self.assertEqual(1, result["warning_count"], result)
        self.assertLess(result["score"], 100, result)
        self.assert_has_check(result, "source_map")

    def test_oversized_agents_md_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(target / "AGENTS.md", "# Oversized\n\n" + ("Verify tests and security. Do not read secrets.\n" * 1200))

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "agents_md_size")


if __name__ == "__main__":
    unittest.main()

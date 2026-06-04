import importlib.util
from unittest.mock import patch
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = REPO_ROOT / "scripts" / "eval_generated_harness.py"
SMOKE_PATH = REPO_ROOT / "scripts" / "smoke_generated_harness.py"
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses"
DETERMINISTIC_PROFILES = [
    "api-design",
    "book-publishing",
    "course-design",
    "customer-support",
    "data-analysis",
    "data-engineering",
    "data-science",
    "devops-infrastructure",
    "financial-modeling",
    "game-development",
    "grant-writing",
    "hiring-pipeline",
    "knowledge-work",
    "legal-research",
    "llm-app",
    "market-research",
    "product-management",
    "security-audit",
    "social-media",
    "software-development",
]
HIGH_RISK_PROFILE_GUIDANCE = {
    "customer-support": (
        "protect customer privacy",
        "pii",
        "human review",
        "do not promise",
    ),
    "financial-modeling": (
        "not financial advice",
        "investment advice",
        "scenario",
        "risk",
    ),
    "hiring-pipeline": (
        "bias",
        "protected class",
        "scorecards",
        "human review",
    ),
    "legal-research": (
        "jurisdiction",
        "not legal advice",
        "cite sources",
        "attorney",
    ),
    "security-audit": (
        "secrets",
        "authorization",
        "active testing",
        "destructive work",
    ),
}

spec = importlib.util.spec_from_file_location("eval_generated_harness", EVAL_PATH)
eval_generated_harness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = eval_generated_harness
spec.loader.exec_module(eval_generated_harness)

smoke_spec = importlib.util.spec_from_file_location("smoke_generated_harness", SMOKE_PATH)
smoke_generated_harness = importlib.util.module_from_spec(smoke_spec)
assert smoke_spec.loader is not None
sys.modules[smoke_spec.name] = smoke_generated_harness
smoke_spec.loader.exec_module(smoke_generated_harness)


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

    def test_local_harness_check_script_accepts_all_fixtures(self):
        for fixture in self.fixture_paths():
            with self.subTest(fixture=fixture.name):
                completed = subprocess.run(
                    [sys.executable, "scripts/check-harness.py"],
                    cwd=fixture,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
                self.assertIn('"status": "pass"', completed.stdout)

    def test_codex_live_smoke_uses_non_interactive_exec(self):
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="OK\n", stderr="")
        with patch.object(smoke_generated_harness.shutil, "which", return_value="/usr/local/bin/codex"):
            with patch.object(smoke_generated_harness.subprocess, "run", return_value=completed) as run:
                result = smoke_generated_harness.smoke_codex_live(Path("/tmp/example"), "Reply OK")

        self.assertEqual("pass", result["status"])
        command = run.call_args.args[0]
        self.assertEqual("/usr/local/bin/codex", command[0])
        self.assertEqual("exec", command[1])
        self.assertIn("--config", command)
        self.assertIn('approval_policy="never"', command)
        self.assertIn("--skip-git-repo-check", command)
        self.assertIn("--ephemeral", command)
        self.assertNotIn("--ask-for-approval", command)

    def test_minimal_generator_lists_supported_profiles(self):
        completed = subprocess.run(
            [sys.executable, "scripts/generate_minimal_harness.py", "--list-profiles"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertEqual(DETERMINISTIC_PROFILES, completed.stdout.strip().splitlines())

    def test_minimal_generator_outputs_pass_eval_and_smoke_for_each_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            targets = []
            for profile in DETERMINISTIC_PROFILES:
                target = Path(temp_dir) / profile
                targets.append(target)
                generate = subprocess.run(
                    [
                        sys.executable,
                        "scripts/generate_minimal_harness.py",
                        target.as_posix(),
                        "--profile",
                        profile,
                    ],
                    cwd=REPO_ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, generate.returncode, generate.stdout + generate.stderr)

                result = eval_generated_harness.evaluate(target)
                self.assertEqual("pass", result["status"], result)
                self.assertGreaterEqual(result["score"], 90, result)

            smoke = subprocess.run(
                [
                    sys.executable,
                    "scripts/smoke_generated_harness.py",
                    "--json",
                    *[target.as_posix() for target in targets],
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, smoke.returncode, smoke.stdout + smoke.stderr)
            self.assertIn('"status": "pass"', smoke.stdout)

    def test_high_risk_profiles_include_domain_guardrail_guidance(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for profile, snippets in HIGH_RISK_PROFILE_GUIDANCE.items():
                with self.subTest(profile=profile):
                    target = Path(temp_dir) / profile
                    generate = subprocess.run(
                        [
                            sys.executable,
                            "scripts/generate_minimal_harness.py",
                            target.as_posix(),
                            "--profile",
                            profile,
                            "--generated-date",
                            "2026-06-04",
                        ],
                        cwd=REPO_ROOT,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, generate.returncode, generate.stdout + generate.stderr)

                    agents_md = (target / "AGENTS.md").read_text(encoding="utf-8").lower()
                    self.assertIn("## domain guidance", agents_md)
                    for snippet in snippets:
                        self.assertIn(snippet, agents_md)

    def test_minimal_generator_supports_fixed_generated_date(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "generated"
            generate = subprocess.run(
                [
                    sys.executable,
                    "scripts/generate_minimal_harness.py",
                    target.as_posix(),
                    "--generated-date",
                    "2026-06-04",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, generate.returncode, generate.stdout + generate.stderr)
            getting_started = (target / "Docs/GETTING_STARTED.md").read_text(encoding="utf-8")
            self.assertIn("Generated: 2026-06-04", getting_started)

    def test_refresh_deterministic_examples_outputs_valid_harnesses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            example_root = Path(temp_dir) / "examples"
            refresh = subprocess.run(
                [
                    sys.executable,
                    "scripts/refresh_deterministic_examples.py",
                    "--example-root",
                    example_root.as_posix(),
                    "--generated-date",
                    "2026-06-04",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, refresh.returncode, refresh.stdout + refresh.stderr)

            generated = sorted(path for path in example_root.iterdir() if path.is_dir())
            self.assertEqual(DETERMINISTIC_PROFILES, [path.name for path in generated])
            for target in generated:
                result = eval_generated_harness.evaluate(target)
                self.assertEqual("pass", result["status"], result)
                self.assertEqual(100, result["score"], result)

    def test_minimal_generator_rejects_non_empty_target_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "generated"
            target.mkdir()
            write(target / "existing.txt", "keep me\n")
            generate = subprocess.run(
                [
                    sys.executable,
                    "scripts/generate_minimal_harness.py",
                    target.as_posix(),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, generate.returncode, generate.stdout + generate.stderr)
            self.assertIn("Target is not empty", generate.stderr)

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

    def test_missing_local_check_script_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        (target / "scripts/check-harness.py").unlink()

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "required_path")

    def test_missing_eval_plan_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        (target / "Docs/Environment/EVAL_PLAN.md").unlink()

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "required_path")

    def test_weak_eval_plan_warns(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        eval_plan = target / "Docs/Environment/EVAL_PLAN.md"
        eval_plan.write_text("# Eval Plan\n\n- Run something eventually.\n", encoding="utf-8")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("pass", result["status"], result)
        self.assertGreater(result["warning_count"], 0, result)
        self.assertLess(result["score"], 100, result)
        self.assert_has_check(result, "eval_plan")

    def test_missing_improvement_log_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        (target / "Docs/Environment/IMPROVEMENT_LOG.md").unlink()

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "required_path")

    def test_weak_improvement_log_warns(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        improvement_log = target / "Docs/Environment/IMPROVEMENT_LOG.md"
        improvement_log.write_text("# Improvement Log\n\n- Write ideas here.\n", encoding="utf-8")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("pass", result["status"], result)
        self.assertGreater(result["warning_count"], 0, result)
        self.assertLess(result["score"], 100, result)
        self.assert_has_check(result, "improvement_log")

    def test_missing_assumptions_ledger_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        (target / "Docs/Environment/ASSUMPTIONS.md").unlink()

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "required_path")

    def test_weak_assumptions_ledger_warns(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        assumptions = target / "Docs/Environment/ASSUMPTIONS.md"
        assumptions.write_text("# Assumptions\n\n- Assumption: This fixture is compact.\n", encoding="utf-8")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("pass", result["status"], result)
        self.assertGreater(result["warning_count"], 0, result)
        self.assertLess(result["score"], 100, result)
        self.assert_has_check(result, "assumptions")

    def test_manifest_reference_to_missing_file_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        manifest = target / "Docs/Environment/MANIFEST.md"
        manifest.write_text(manifest.read_text(encoding="utf-8") + "- missing/file.md\n", encoding="utf-8")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "manifest_reference")

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

    def test_custom_permission_profile_without_extends_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace('extends = ":workspace"\n', ""),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "config_permissions")

    def test_invalid_filesystem_permission_value_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace('"." = "write"', '"." = "allow"'),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "permission_values")

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

    def test_hook_event_singleton_table_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8")
            + '\n[features]\nhooks = true\n\n[hooks.InstructionsLoaded]\ncommand = "echo loaded"\n',
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "hooks_config")

    def test_skill_config_without_enabled_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        config = target / ".codex/config.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("enabled = true\n", ""),
            encoding="utf-8",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"])
        self.assert_has_check(result, "skills_config")

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

    def test_security_audit_fixture_satisfies_high_risk_guardrails(self):
        result = eval_generated_harness.evaluate(FIXTURES_ROOT / "security-audit-basic")

        checks = {finding["check"] for finding in result["findings"]}
        self.assertEqual("pass", result["status"], result)
        self.assertNotIn("domain_guardrails", checks)

    def test_security_audit_without_active_testing_boundary_fails(self):
        temp_dir, target = self.copy_fixture("security-audit-basic")
        self.addCleanup(temp_dir.cleanup)
        agents = target / "AGENTS.md"
        agents.write_text(
            agents.read_text(encoding="utf-8")
            .replace("exploitable", "important")
            .replace("- Ask for clarification before active testing or destructive work.\n", ""),
            encoding="utf-8",
        )
        for path in target.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".toml"}:
                text = path.read_text(encoding="utf-8")
                text = text.replace("active testing", "extra work")
                text = text.replace("destructive", "broad")
                text = text.replace("exploit", "issue")
                path.write_text(text, encoding="utf-8")

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"], result)
        self.assert_has_check(result, "domain_guardrails")

    def test_legal_research_without_jurisdiction_boundary_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(
            target / "AGENTS.md",
            "# Legal Research Harness\n\nVerify sources, run tests when available, do not read secrets, and treat security seriously.\n",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"], result)
        self.assert_has_check(result, "domain_guardrails")

    def test_financial_modeling_without_advice_boundary_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(
            target / "AGENTS.md",
            "# Financial Modeling Harness\n\nVerify assumptions, run tests when available, do not read secrets, and treat security seriously.\n",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"], result)
        self.assert_has_check(result, "domain_guardrails")

    def test_hiring_pipeline_without_bias_guardrail_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(
            target / "AGENTS.md",
            "# Hiring Pipeline Harness\n\nVerify criteria, run tests when available, do not read secrets, and treat security seriously.\n",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"], result)
        self.assert_has_check(result, "domain_guardrails")

    def test_customer_support_without_escalation_path_fails(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        write(
            target / "AGENTS.md",
            "# Customer Support Harness\n\nVerify source notes, run tests when available, do not read secrets, and treat security and privacy seriously.\n",
        )

        result = eval_generated_harness.evaluate(target)
        self.assertEqual("fail", result["status"], result)
        self.assert_has_check(result, "domain_guardrails")


if __name__ == "__main__":
    unittest.main()

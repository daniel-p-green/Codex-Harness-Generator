import importlib.util
import textwrap
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = REPO_ROOT / "scripts" / "eval_codex_port.py"

spec = importlib.util.spec_from_file_location("eval_codex_port", EVAL_PATH)
eval_codex_port = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(eval_codex_port)


OFFICIAL_SOURCE_TEXT = """
- https://developers.openai.com/codex/concepts/customization
- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/config-reference
- https://developers.openai.com/codex/subagents
- https://developers.openai.com/codex/permissions
- https://developers.openai.com/codex/skills
- https://developers.openai.com/api/docs/guides/reasoning
"""


AGENT_TOML = """
name = "{name}"
description = "Specialized Codex subagent for {name} work."
model = "gpt-5.5"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
developer_instructions = \"\"\"
Do focused Codex work and report concise results.
\"\"\"
"""


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def build_green_repo(root: Path) -> None:
    write(
        root / "README.md",
        """
        # Codex Harness Generator

        This OpenAI Codex project generates AGENTS.md, .codex/config.toml,
        .agents/skills, MCP guidance, custom subagents, and gpt-5.5 defaults.
        """,
    )
    write(
        root / "AGENTS.md",
        """
        # AGENTS.md

        Use .codex/config.toml, .agents/skills, and gpt-5.5 for this OpenAI
        Codex harness generator.
        """,
    )
    write(
        root / "Docs/OVERVIEW.md",
        """
        # Overview

        This OpenAI Codex port uses AGENTS.md, .codex/config.toml,
        .agents/skills, model_reasoning_effort, MCP, subagents, and gpt-5.5.
        """,
    )
    write(root / "Docs/Environment/MANIFEST.md", "# Manifest\n")
    write(root / "Docs/Templates/Core/agents-md.md", "# AGENTS.md Template\n")
    write(root / "Docs/Templates/Core/codex-config-toml.md", "# Config Template\n")
    write(root / "Docs/Environment/CODEX_PORT_EVALUATION.md", OFFICIAL_SOURCE_TEXT)

    write(
        root / ".codex/config.toml",
        """
        model = "gpt-5.5"
        model_reasoning_effort = "medium"
        default_permissions = "project-default"

        [agents]
        max_threads = 6
        max_depth = 1

        [agents.intake-interviewer]
        description = "Conducts project intake."
        config_file = "agents/intake-interviewer.toml"

        [agents.environment-architect]
        description = "Designs Codex environment architecture."
        config_file = "agents/environment-architect.toml"

        [agents.component-generator]
        description = "Generates Codex environment files."
        config_file = "agents/component-generator.toml"

        [agents.environment-validator]
        description = "Validates generated Codex environments."
        config_file = "agents/environment-validator.toml"

        [agents.upgrade-analyzer]
        description = "Audits existing Codex environments."
        config_file = "agents/upgrade-analyzer.toml"

        [[skills.config]]
        path = "../.agents/skills/create"
        enabled = true

        [[skills.config]]
        path = "../.agents/skills/validate-environment"
        enabled = true

        [[skills.config]]
        path = "../.agents/skills/upgrade-environment"
        enabled = true

        [[skills.config]]
        path = "../.agents/skills/update"
        enabled = true

        [permissions.project-default]
        description = "Project permissions."
        extends = ":workspace"

        [permissions.project-default.filesystem]
        glob_scan_max_depth = 4

        [permissions.project-default.filesystem.":workspace_roots"]
        "." = "write"
        "**/.env" = "deny"
        "**/.env.*" = "deny"
        "**/*secret*" = "deny"
        "**/*token*" = "deny"
        "**/*credential*" = "deny"
        "**/*.pem" = "deny"
        "**/*.key" = "deny"

        [permissions.project-default.network]
        enabled = true
        mode = "limited"

        [permissions.project-default.network.domains]
        "developers.openai.com" = "allow"
        """,
    )

    for name in [
        "intake-interviewer",
        "environment-architect",
        "component-generator",
        "environment-validator",
        "upgrade-analyzer",
    ]:
        write(root / f".codex/agents/{name}.toml", AGENT_TOML.format(name=name))

    for skill_name in [
        "create",
        "validate-environment",
        "upgrade-environment",
        "update",
    ]:
        write(
            root / f".agents/skills/{skill_name}/SKILL.md",
            f"""
            ---
            name: {skill_name}
            description: Runs Codex harness {skill_name} workflows with deterministic setup and validation steps. Use when the user explicitly asks for {skill_name}, harness setup, harness validation, harness upgrade, or knowledge refresh work.
            ---

            Run the deterministic workflow for this Codex harness task.
            """,
        )

    write(
        root / "Docs/Templates/Agents/reviewer.md",
        """
        # Reviewer

        ```toml
        name = "reviewer"
        description = "Reviews Codex harness changes."
        model = "gpt-5.5"
        model_reasoning_effort = "high"
        sandbox_mode = "read-only"
        developer_instructions = \"\"\"
        Review changes for correctness and risk.
        \"\"\"
        ```
        """,
    )


class EvalCodexPortTests(unittest.TestCase):
    def run_eval(self, mutate=None):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_green_repo(root)
            if mutate:
                mutate(root)
            return eval_codex_port.collect_failures(root)

    def assert_fails_check(self, failures, check):
        checks = {failure["check"] for failure in failures}
        self.assertIn(check, checks, failures)

    def test_green_fixture_passes(self):
        self.assertEqual([], self.run_eval())

    def test_legacy_root_instruction_file_fails(self):
        failures = self.run_eval(lambda root: write(root / "CLAUDE.md", "# Old\n"))
        self.assert_fails_check(failures, "forbidden_path")

    def test_legacy_tool_name_fails(self):
        def mutate(root: Path) -> None:
            with (root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\nUse WebSearch for docs lookups.\n")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "forbidden_text")

    def test_missing_required_codex_path_fails(self):
        failures = self.run_eval(lambda root: (root / "AGENTS.md").unlink())
        self.assert_fails_check(failures, "required_path")

    def test_permission_profile_conflict_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            path.write_text(
                'sandbox_mode = "workspace-write"\n' + path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_permissions")

    def test_nested_default_permissions_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace('default_permissions = "project-default"\n\n', "")
            text += '\ndefault_permissions = "project-default"\n'
            path.write_text(text, encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_permissions")

    def test_missing_agent_schema_field_fails(self):
        def mutate(root: Path) -> None:
            write(
                root / ".codex/agents/upgrade-analyzer.toml",
                """
                name = "upgrade-analyzer"
                description = "Analyzes upgrade work."
                model = "gpt-5.5"
                model_reasoning_effort = "high"
                sandbox_mode = "read-only"
                """,
            )

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "agent_schema")

    def test_invalid_embedded_agent_toml_fails(self):
        failures = self.run_eval(
            lambda root: write(
                root / "Docs/Templates/Agents/broken.md",
                """
                # Broken

                ```toml
                name = "broken"
                model = "gpt-5.5
                ```
                """,
            )
        )
        self.assert_fails_check(failures, "embedded_agent_toml")

    def test_missing_official_source_fails(self):
        failures = self.run_eval(
            lambda root: write(root / "Docs/Environment/CODEX_PORT_EVALUATION.md", "# Empty\n")
        )
        self.assert_fails_check(failures, "official_source")

    def test_invalid_root_reasoning_effort_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace('model_reasoning_effort = "medium"', 'model_reasoning_effort = "huge"'), encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_reasoning")

    def test_missing_skills_config_target_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace('path = "../.agents/skills/update"', 'path = "../.agents/skills/missing"')
            path.write_text(text, encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_skills")

    def test_missing_agent_registry_target_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace('config_file = "agents/upgrade-analyzer.toml"', 'config_file = "agents/missing.toml"')
            path.write_text(text, encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "agent_registry")

    def test_agent_name_mismatch_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/agents/upgrade-analyzer.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace('name = "upgrade-analyzer"', 'name = "wrong-agent"'), encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "agent_schema")

    def test_missing_skill_metadata_fails(self):
        def mutate(root: Path) -> None:
            write(root / ".agents/skills/update/SKILL.md", "# Update\n")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "skill_metadata")

    def test_recursive_deny_without_glob_depth_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace("[permissions.project-default.filesystem]\nglob_scan_max_depth = 4\n\n", "")
            path.write_text(text, encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_permissions")

    def test_custom_permission_profile_without_extends_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace('extends = ":workspace"\n', ""))

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_permissions")

    def test_invalid_filesystem_permission_value_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace('"." = "write"', '"." = "allow"'))

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_permissions")

    def test_agent_web_search_requires_broad_network_policy(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/agents/intake-interviewer.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace("Do focused Codex work", "Search the web when needed. Do focused Codex work")
            path.write_text(text, encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "agent_network_policy")

    def test_hooks_enabled_without_hooks_config_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            text = text.replace("[agents]\n", "[features]\nhooks = true\n\n[agents]\n")
            path.write_text(text, encoding="utf-8")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_hooks")

    def test_hook_event_singleton_table_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text + '\n[features]\nhooks = true\n\n[hooks.InstructionsLoaded]\ncommand = "echo loaded"\n')

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_hooks")

    def test_skill_config_without_enabled_fails(self):
        def mutate(root: Path) -> None:
            path = root / ".codex/config.toml"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("enabled = true\n", ""))

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "codex_config_skills")

    def test_legacy_text_in_python_source_fails(self):
        def mutate(root: Path) -> None:
            write(root / "scripts/example.py", "print('Use WebSearch here')\n")

        failures = self.run_eval(mutate)
        self.assert_fails_check(failures, "forbidden_text")


if __name__ == "__main__":
    unittest.main()

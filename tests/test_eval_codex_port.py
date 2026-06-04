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

        [permissions.project-default]
        description = "Project permissions."
        extends = ":workspace"

        [permissions.project-default.filesystem.":workspace_roots"]
        "." = "write"

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
            description: Use for Codex harness {skill_name} workflows.
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


if __name__ == "__main__":
    unittest.main()

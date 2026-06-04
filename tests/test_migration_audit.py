import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATION_AUDIT_PATH = REPO_ROOT / "scripts" / "migration_audit.py"

spec = importlib.util.spec_from_file_location("migration_audit", MIGRATION_AUDIT_PATH)
migration_audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = migration_audit
spec.loader.exec_module(migration_audit)


def write(path: Path, text: str = "ok\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_codex_ready(root: Path) -> None:
    write(root / "AGENTS.md")
    write(root / ".codex/config.toml")
    write(root / ".codex/agents/reviewer.toml")
    write(root / ".agents/skills/health-check/SKILL.md")


class MigrationAuditTests(unittest.TestCase):
    def test_codex_ready_harness_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_codex_ready(root)

            payload = migration_audit.build_payload([root.as_posix()])

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("pass", payload["results"][0]["status"])
        self.assertEqual([], payload["results"][0]["findings"])
        self.assertEqual("codex-native", payload["results"][0]["migration_plan"]["readiness"])
        self.assertTrue(any("codex-harness validate" in command for command in payload["results"][0]["migration_plan"]["commands"]))

    def test_legacy_harness_reports_migration_findings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "CLAUDE.md", "# Legacy instructions\n")
            write(root / ".claude/settings.json", '{"allowed-tools": ["WebSearch"]}\n')
            write(root / ".claude/agents/reviewer.md", "---\nmaxTurns: 5\n---\n")

            payload = migration_audit.build_payload([root.as_posix()])

        self.assertEqual("needs_migration", payload["status"])
        result = payload["results"][0]
        self.assertEqual("needs_migration", result["status"])
        kinds = {finding["kind"] for finding in result["findings"]}
        self.assertIn("legacy_path", kinds)
        self.assertIn("missing_codex_path", kinds)
        self.assertIn("legacy_text", kinds)
        recommendations = "\n".join(finding["recommendation"] for finding in result["findings"])
        self.assertIn("AGENTS.md", recommendations)
        self.assertIn(".codex/config.toml", recommendations)
        self.assertEqual("needs-manual-migration", result["migration_plan"]["readiness"])
        commands = "\n".join(result["migration_plan"]["commands"])
        self.assertIn("codex-harness init", commands)
        self.assertIn("codex-harness adoption-plan", commands)
        self.assertIn("codex-harness validate", commands)
        self.assertIn("CLAUDE.md", "\n".join(result["migration_plan"]["manual_steps"]))

    def test_main_json_returns_nonzero_for_legacy_harness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "CLAUDE.md")
            output = io.StringIO()

            with redirect_stdout(output):
                status = migration_audit.main([root.as_posix(), "--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(1, status)
        self.assertEqual("needs_migration", payload["status"])

    def test_text_output_includes_next_steps(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "CLAUDE.md")
            output = io.StringIO()

            with redirect_stdout(output):
                status = migration_audit.main([root.as_posix()])

        text = output.getvalue()
        self.assertEqual(1, status)
        self.assertIn("Migration audit: NEEDS_MIGRATION", text)
        self.assertIn("next:", text)
        self.assertIn("command:", text)

    def test_main_writes_markdown_migration_plan_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "legacy"
            write(root / "CLAUDE.md")
            report = Path(temp_dir) / "CODEX_MIGRATION_PLAN.md"
            output = io.StringIO()

            with redirect_stdout(output):
                status = migration_audit.main([root.as_posix(), "--report", report.as_posix()])
            report_text = report.read_text(encoding="utf-8")

        self.assertEqual(1, status)
        self.assertIn("# Codex Migration Plan", report_text)
        self.assertIn("Migration readiness: needs-manual-migration", report_text)
        self.assertIn("codex-harness adoption-plan", report_text)
        self.assertIn("CLAUDE.md", report_text)

    def test_no_write_skips_markdown_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "legacy"
            write(root / "CLAUDE.md")
            report = Path(temp_dir) / "CODEX_MIGRATION_PLAN.md"
            output = io.StringIO()

            with redirect_stdout(output):
                status = migration_audit.main([root.as_posix(), "--report", report.as_posix(), "--no-write"])

        self.assertEqual(1, status)
        self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main()

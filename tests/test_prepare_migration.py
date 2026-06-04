import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "prepare_migration.py"
LEGACY_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "legacy_harnesses" / "legacy-basic"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("prepare_migration", SCRIPT)
prepare_migration = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = prepare_migration
spec.loader.exec_module(prepare_migration)


class PrepareMigrationTests(unittest.TestCase):
    def copy_legacy_fixture(self, temp_path: Path) -> Path:
        source = temp_path / "legacy-basic"
        shutil.copytree(LEGACY_FIXTURE, source)
        return source

    def test_build_payload_writes_migration_packet_and_copy_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = self.copy_legacy_fixture(temp_path)
            output = temp_path / "migration-packet"
            args = Namespace(
                source=source.as_posix(),
                output=output.as_posix(),
                profile="software-development",
                project_name="Legacy Basic Codex Harness",
                source_label="public legacy fixture",
                max_files=100,
                limit=3,
                generated_date="2026-06-04",
                generated="2026-06-04T12:00:00Z",
                force=False,
            )

            payload = prepare_migration.build_payload(args)
            copy_completed = subprocess.run(
                [payload["copy_script"]],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual("pass", payload["status"])
            self.assertEqual("needs-manual-migration", payload["migration_readiness"])
            self.assertEqual("software-development", payload["profile"])
            self.assertGreater(payload["migration_failures"], 0)
            self.assertGreater(payload["adoption_summary"]["add"], 0)
            self.assertTrue(Path(payload["migration_report"]).exists())
            self.assertTrue(Path(payload["adoption_report"]).exists())
            self.assertTrue(Path(payload["readme"]).exists())
            self.assertTrue((Path(payload["blueprint"]) / "AGENTS.md").exists())
            self.assertTrue(Path(payload["copy_script"]).stat().st_mode & 0o111)
            self.assertEqual(0, copy_completed.returncode, copy_completed.stdout + copy_completed.stderr)
            self.assertTrue((source / "AGENTS.md").exists())
            self.assertTrue((source / "CLAUDE.md").exists())
            self.assertIn("Preparing a migration packet is not proof", payload["claim_boundary"])

    def test_refuses_non_empty_output_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = self.copy_legacy_fixture(temp_path)
            output = temp_path / "migration-packet"
            (output / "README.md").parent.mkdir(parents=True)
            (output / "README.md").write_text("existing\n", encoding="utf-8")
            args = Namespace(
                source=source.as_posix(),
                output=output.as_posix(),
                profile=None,
                project_name=None,
                source_label=None,
                max_files=100,
                limit=3,
                generated_date="2026-06-04",
                generated="2026-06-04T12:00:00Z",
                force=False,
            )

            with self.assertRaises(SystemExit) as raised:
                prepare_migration.build_payload(args)

        self.assertIn("Output directory is not empty", str(raised.exception))

    def test_cli_emits_json_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = self.copy_legacy_fixture(temp_path)
            output = temp_path / "migration-packet"

            completed = subprocess.run(
                [
                    sys.executable,
                    SCRIPT.as_posix(),
                    source.as_posix(),
                    output.as_posix(),
                    "--source-label",
                    "public legacy fixture",
                    "--generated",
                    "2026-06-04T12:00:00Z",
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
        self.assertEqual("public legacy fixture", payload["source_label"])
        self.assertTrue(payload["copy_script"].endswith("copy-codex-harness-adds.sh"))


if __name__ == "__main__":
    unittest.main()

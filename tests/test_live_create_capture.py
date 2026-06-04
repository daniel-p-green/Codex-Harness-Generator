import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURE_PATH = REPO_ROOT / "scripts" / "capture_live_create_example.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("capture_live_create_example", CAPTURE_PATH)
capture_live_create_example = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = capture_live_create_example
spec.loader.exec_module(capture_live_create_example)


class LiveCreateCaptureTests(unittest.TestCase):
    def test_capture_existing_generated_target_writes_sanitized_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            generated = temp_root / "generated"
            output_root = temp_root / "live-create"

            create = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_create_acceptance.py",
                    generated.as_posix(),
                    "--profile",
                    "software-development",
                    "--project-name",
                    "Synthetic Cleanup CLI",
                    "--project-type",
                    "Python CLI",
                    "--notes",
                    "synthetic live-create capture test",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, create.returncode, create.stdout + create.stderr)

            (generated / ".env").write_text("SECRET=do-not-copy\n", encoding="utf-8")
            (generated / "Docs/_working/state").mkdir(parents=True)
            (generated / "Docs/_working/state/SESSION_CONTEXT.md").write_text("transient\n", encoding="utf-8")
            payload = capture_live_create_example.capture_live_example(
                target=generated,
                capture_name="Synthetic Cleanup CLI",
                project_brief="Synthetic Python CLI utility for local file cleanup",
                output_root=output_root,
                force=True,
                run_codex=False,
                timeout=30,
                model=None,
                captured="2026-06-04T12:00:00Z",
                source_label="temporary synthetic target",
                allow_missing_creation_context=False,
                project_type="Python CLI",
                notes="synthetic live-create capture test",
            )

            capture = output_root / "synthetic-cleanup-cli"
            self.assertEqual("pass", payload["status"], payload)
            self.assertTrue((capture / "AGENTS.md").is_file())
            self.assertFalse((capture / ".env").exists())
            self.assertFalse((capture / "Docs/_working").exists())
            architecture = (capture / "Docs/Environment/ARCHITECTURE.md").read_text(encoding="utf-8")
            self.assertNotIn("Docs/_working/", architecture)
            report = capture / "Docs/Environment/LIVE_CREATE_CAPTURE.md"
            self.assertTrue(report.is_file())
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("Status: PASS.", report_text)
            self.assertIn("- Mode: existing generated target", report_text)
            context = capture / "Docs/Environment/CREATION_CONTEXT.md"
            context_text = context.read_text(encoding="utf-8")
            self.assertIn("- Path: temporary synthetic target", context_text)
            self.assertNotIn(generated.as_posix(), context_text)
            self.assertNotIn(generated.resolve().as_posix(), context_text)
            self.assertNotIn(" from /", context_text)
            manifest = (capture / "Docs/Environment/MANIFEST.md").read_text(encoding="utf-8")
            self.assertIn("- Docs/Environment/LIVE_CREATE_CAPTURE.md", manifest)
            self.assertNotIn("Docs/_working/", manifest)

    def test_run_codex_create_uses_constrained_non_interactive_command(self):
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="created\n", stderr="")
        target = Path("/tmp/codex-live-target")

        with patch.object(capture_live_create_example.shutil, "which", return_value="/usr/local/bin/codex"):
            with patch.object(capture_live_create_example.subprocess, "run", return_value=completed) as run:
                result = capture_live_create_example.run_codex_create(
                    target=target,
                    project_brief="Synthetic docs workspace",
                    project_type="Knowledge work",
                    notes="public-safe docs capture",
                    source_label="temporary synthetic target",
                    timeout=60,
                    model="gpt-5.5-codex",
                )

        self.assertEqual(0, result["returncode"])
        command = run.call_args.args[0]
        prompt = command[-1]
        self.assertEqual("/usr/local/bin/codex", command[0])
        self.assertEqual("exec", command[1])
        self.assertIn("--cd", command)
        self.assertIn("--add-dir", command)
        self.assertIn("--sandbox", command)
        self.assertIn("workspace-write", command)
        self.assertIn("--config", command)
        self.assertIn('approval_policy="never"', command)
        self.assertIn("--ephemeral", command)
        self.assertNotIn("--ask-for-approval", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
        self.assertIn("/tmp/codex-live-target", prompt)
        self.assertIn("/create", prompt)
        self.assertIn("CREATION_CONTEXT.md", prompt)
        self.assertIn("generate_minimal_harness.py", prompt)
        self.assertIn("Synthetic docs workspace", prompt)
        self.assertIn("--project-type 'Knowledge work'", prompt)
        self.assertIn("--notes 'public-safe docs capture'", prompt)
        self.assertIn("--target-label 'temporary synthetic target'", prompt)


if __name__ == "__main__":
    unittest.main()

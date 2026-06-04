import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_evidence_packet.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses" / "software-dev-basic"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_evidence_packet", SCRIPT)
export_evidence_packet = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_evidence_packet
spec.loader.exec_module(export_evidence_packet)


class ExportEvidencePacketTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp_dir = tempfile.TemporaryDirectory()
        target = Path(temp_dir.name) / "harness"
        shutil.copytree(FIXTURE, target)
        return temp_dir, target

    def record_trial(self, target: Path) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/record-task-trial.py",
                "--date",
                "2026-06-04",
                "--task",
                "Evidence packet smoke",
                "--outcome",
                "success",
                "--evidence",
                "Generated evidence packet was inspected.",
                "--verification",
                "python scripts/run-harness-evals.py",
                "--privacy-review",
                "Synthetic public-safe test only.",
                "--harness-helped",
                "The harness required verification before evidence export.",
                "--limitations",
                "One synthetic copied-harness task.",
            ],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def test_exports_public_safe_packet_from_copied_harness(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)
        packet = Path(temp_dir.name) / "packet.md"

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--out",
                packet.as_posix(),
                "--harness-label",
                "synthetic copied harness",
                "--min-successes",
                "1",
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
        self.assertEqual("synthetic copied harness", payload["harness"])
        self.assertEqual(1, payload["task_trials"]["complete"])
        text = packet.read_text(encoding="utf-8")
        self.assertIn("# Generated Harness Evidence Packet", text)
        self.assertIn("Evidence packet smoke", text)
        self.assertIn("Retain raw evidence privately", text)

    def test_packet_marks_failed_threshold_as_needs_review(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)

        payload = export_evidence_packet.build_payload(target, min_successes=2, harness_label="threshold test")

        self.assertEqual("needs-review", payload["status"])
        self.assertIn("success count 1 is below required minimum 2", payload["issues"])

    def test_rejects_sensitive_packet_text(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        trials = target / "Docs" / "Environment" / "TASK_TRIALS.md"
        trials.write_text(
            trials.read_text(encoding="utf-8")
            + "\n".join(
                [
                    "### 2026-06-04 - SUCCESS - Sensitive trial",
                    "",
                    "- Task: Sensitive trial",
                    "- Outcome: success",
                    "- Evidence: Contact alice@example.com for raw evidence.",
                    "- Verification: python scripts/run-harness-evals.py",
                    "- Privacy review: Synthetic public-safe test only.",
                    "- Harness helped: The harness required verification.",
                    "- Limitations: One synthetic copied-harness task.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        with self.assertRaises(SystemExit) as raised:
            export_evidence_packet.build_payload(target, min_successes=0, harness_label="sensitive test")

        self.assertIn("sensitive text", str(raised.exception))


if __name__ == "__main__":
    unittest.main()

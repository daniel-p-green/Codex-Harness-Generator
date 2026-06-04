import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "usage_from_harness.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses" / "software-dev-basic"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("usage_from_harness", SCRIPT)
usage_from_harness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = usage_from_harness
spec.loader.exec_module(usage_from_harness)

import pilot_board


class UsageFromHarnessTests(unittest.TestCase):
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
                "Usage proof smoke",
                "--outcome",
                "success",
                "--evidence",
                "Generated usage proof report was inspected.",
                "--verification",
                "python scripts/run-harness-evals.py",
                "--privacy-review",
                "Synthetic public-safe test only.",
                "--harness-helped",
                "The harness required verification before evidence capture.",
                "--limitations",
                "One synthetic copied-harness task.",
            ],
            cwd=target,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)

    def write_matching_pilot_record(self, pilot_record_dir: Path, domain: str = "software development") -> Path:
        payload = {
            "generated": "2026-06-04T00:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": "usage-proof-smoke",
                "title": "Usage proof smoke",
                "domain": domain,
                "profile": "software-development",
                "source_type": "external",
                "generation_path": "installed-init-brief",
                "project_name": "Usage Proof Pilot",
            },
            "prepared_pilot": {
                "target": "/tmp/usage-proof-smoke",
                "pilot_pack": {
                    "harness_label": "synthetic copied harness",
                    "pack": "/tmp/PILOT_PACK.md",
                    "issue_draft": "/tmp/ISSUE.md",
                },
            },
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
        }
        pilot_record_dir.mkdir(parents=True, exist_ok=True)
        record_path = pilot_record_dir / "usage-proof-smoke.json"
        pilot_board.write_record(record_path, pilot_board.build_record(payload), force=True)
        return record_path

    def test_usage_from_harness_writes_privacy_checked_record(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)
        record_dir = Path(temp_dir.name) / "records"
        report = Path(temp_dir.name) / "USAGE_RECORDS.md"

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "usage-proof-smoke",
                "--title",
                "Usage proof smoke",
                "--domain",
                "software development",
                "--harness-label",
                "synthetic copied harness",
                "--evidence-type",
                "synthetic",
                "--source-type",
                "self-dogfood",
                "--generation-path",
                "installed-init-brief",
                "--privacy-review",
                "Synthetic public-safe test only.",
                "--record-dir",
                record_dir.as_posix(),
                "--report",
                report.as_posix(),
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
        record = payload["record"]
        self.assertEqual("usage-proof-smoke", record["slug"])
        self.assertEqual("success", record["outcome"])
        self.assertEqual("synthetic copied harness", record["harness_path"])
        self.assertEqual("self-dogfood", record["source_type"])
        self.assertEqual("installed-init-brief", record["generation_path"])
        self.assertTrue(any("local eval report status" in item for item in record["evidence"]))
        self.assertTrue(any("Complete task-trial records reviewed: 1" in item for item in record["verification"]))
        self.assertTrue((record_dir / "usage-proof-smoke.json").is_file())
        self.assertIn("usage-proof-smoke", report.read_text(encoding="utf-8"))

    def test_usage_from_harness_can_convert_matching_pilot_record(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)
        temp_path = Path(temp_dir.name)
        record_dir = temp_path / "records"
        report = temp_path / "USAGE_RECORDS.md"
        pilot_record_dir = temp_path / "pilot-records"
        board_report = temp_path / "PILOT_BOARD.md"
        pilot_record_path = self.write_matching_pilot_record(pilot_record_dir)

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "usage-proof-smoke",
                "--title",
                "Usage proof smoke",
                "--domain",
                "software development",
                "--harness-label",
                "synthetic copied harness",
                "--evidence-type",
                "private-summary",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--privacy-review",
                "Public-safe copied-harness evidence only.",
                "--record-dir",
                record_dir.as_posix(),
                "--report",
                report.as_posix(),
                "--pilot-record-dir",
                pilot_record_dir.as_posix(),
                "--pilot-board-report",
                board_report.as_posix(),
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
        self.assertEqual("pass", payload["pilot_update"]["status"])
        self.assertEqual("pass", payload["pilot_update"]["board_status"])
        pilot_record = json.loads(pilot_record_path.read_text(encoding="utf-8"))
        self.assertEqual("converted", pilot_record["status"])
        self.assertEqual("usage-proof-smoke", pilot_record["usage_record"])
        self.assertTrue(pilot_record["validated_usage_record"].endswith("usage-proof-smoke.json"))
        self.assertIn("Converted with validated usage records: 1", board_report.read_text(encoding="utf-8"))

    def test_usage_from_harness_infers_metadata_from_pilot_record(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)
        temp_path = Path(temp_dir.name)
        record_dir = temp_path / "records"
        report = temp_path / "USAGE_RECORDS.md"
        pilot_record_dir = temp_path / "pilot-records"
        self.write_matching_pilot_record(pilot_record_dir)

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "usage-proof-smoke",
                "--evidence-type",
                "private-summary",
                "--privacy-review",
                "Public-safe copied-harness evidence only.",
                "--record-dir",
                record_dir.as_posix(),
                "--report",
                report.as_posix(),
                "--pilot-record-dir",
                pilot_record_dir.as_posix(),
                "--no-write",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        record = payload["record"]
        self.assertFalse(payload["written"])
        self.assertEqual("Usage proof smoke", record["title"])
        self.assertEqual("software development", record["domain"])
        self.assertEqual("synthetic copied harness", record["harness_path"])
        self.assertEqual("external", record["source_type"])
        self.assertEqual("installed-init-brief", record["generation_path"])

    def test_usage_from_harness_no_write_validates_without_writing_record(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)
        temp_path = Path(temp_dir.name)
        record_dir = temp_path / "records"
        report = temp_path / "USAGE_RECORDS.md"
        pilot_record_dir = temp_path / "pilot-records"
        pilot_record_path = self.write_matching_pilot_record(pilot_record_dir)

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "usage-proof-smoke",
                "--title",
                "Usage proof smoke",
                "--domain",
                "software development",
                "--harness-label",
                "synthetic copied harness",
                "--evidence-type",
                "private-summary",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--privacy-review",
                "Public-safe copied-harness evidence only.",
                "--record-dir",
                record_dir.as_posix(),
                "--report",
                report.as_posix(),
                "--pilot-record-dir",
                pilot_record_dir.as_posix(),
                "--no-write",
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
        self.assertFalse(payload["written"])
        self.assertIsNone(payload["path"])
        self.assertEqual("usage-proof-smoke", payload["record"]["slug"])
        self.assertIsNone(payload["pilot_update"])
        self.assertFalse((record_dir / "usage-proof-smoke.json").exists())
        self.assertFalse(report.exists())
        pilot_record = json.loads(pilot_record_path.read_text(encoding="utf-8"))
        self.assertEqual("prepared", pilot_record["status"])
        self.assertEqual("", pilot_record["usage_record"])

    def test_usage_from_harness_rejects_pilot_mismatch_before_writing_record(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)
        temp_path = Path(temp_dir.name)
        record_dir = temp_path / "records"
        report = temp_path / "USAGE_RECORDS.md"
        pilot_record_dir = temp_path / "pilot-records"
        pilot_record_path = self.write_matching_pilot_record(pilot_record_dir, domain="customer support")

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "usage-proof-smoke",
                "--title",
                "Usage proof smoke",
                "--domain",
                "software development",
                "--evidence-type",
                "private-summary",
                "--source-type",
                "external",
                "--generation-path",
                "installed-init-brief",
                "--privacy-review",
                "Public-safe copied-harness evidence only.",
                "--record-dir",
                record_dir.as_posix(),
                "--report",
                report.as_posix(),
                "--pilot-record-dir",
                pilot_record_dir.as_posix(),
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("Pilot conversion validation failed", completed.stderr + completed.stdout)
        self.assertIn("domain mismatch before write", completed.stderr + completed.stdout)
        self.assertFalse((record_dir / "usage-proof-smoke.json").exists())
        self.assertFalse(report.exists())
        pilot_record = json.loads(pilot_record_path.read_text(encoding="utf-8"))
        self.assertEqual("prepared", pilot_record["status"])
        self.assertEqual("", pilot_record["usage_record"])

    def test_usage_from_harness_requires_complete_task_trial(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "missing-trial",
                "--title",
                "Missing trial",
                "--domain",
                "software development",
                "--evidence-type",
                "synthetic",
                "--source-type",
                "self-dogfood",
                "--generation-path",
                "repo-dogfood",
                "--privacy-review",
                "Synthetic public-safe test only.",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("No complete task-trial entries", completed.stderr + completed.stdout)

    def test_usage_from_harness_requires_metadata_without_pilot_record(self):
        temp_dir, target = self.copy_fixture()
        self.addCleanup(temp_dir.cleanup)
        self.record_trial(target)

        completed = subprocess.run(
            [
                sys.executable,
                SCRIPT.as_posix(),
                target.as_posix(),
                "--slug",
                "missing-metadata",
                "--evidence-type",
                "synthetic",
                "--privacy-review",
                "Synthetic public-safe test only.",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("Missing required metadata", completed.stderr + completed.stdout)
        self.assertIn("--title", completed.stderr + completed.stdout)
        self.assertIn("--domain", completed.stderr + completed.stdout)

    def test_derive_outcome_uses_eval_and_task_trial_state(self):
        self.assertEqual("failed", usage_from_harness.derive_outcome("fail", {"success": 1}))
        self.assertEqual("success", usage_from_harness.derive_outcome("pass", {"success": 1}))
        self.assertEqual("partial", usage_from_harness.derive_outcome("pass", {"partial": 1}))
        self.assertEqual("inconclusive", usage_from_harness.derive_outcome("pass", {}))


if __name__ == "__main__":
    unittest.main()

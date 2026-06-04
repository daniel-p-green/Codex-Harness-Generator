import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROOF_STATUS_PATH = REPO_ROOT / "scripts" / "proof_status.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("proof_status", PROOF_STATUS_PATH)
proof_status = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = proof_status
spec.loader.exec_module(proof_status)


class ProofStatusTests(unittest.TestCase):
    def test_parse_task_trials_counts_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "TASK_TRIALS.md"
            path.write_text(
                """# Live Example Task Trials

Status: PASS

| Trial | Example | Status | Output |
|---|---|---|---|
| `one` | `example-one` | PASS | `out.md` |
| `two` | `example-two` | FAIL | `out.md` |
""",
                encoding="utf-8",
            )

            payload = proof_status.parse_task_trials(path)

        self.assertEqual("pass", payload["status"])
        self.assertEqual(2, payload["trial_count"])
        self.assertEqual(1, payload["pass_count"])
        self.assertEqual(["two"], payload["failed_trials"])

    def test_build_payload_passes_with_current_reports_and_usage_record(self):
        payload = proof_status.build_payload(
            min_live_trials=8,
            min_usage_records=1,
            record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
        )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual(8, payload["task_trials"]["trial_count"])
        self.assertEqual("pass", payload["example_inventory"]["status"])
        self.assertEqual(4, payload["example_inventory"]["brief_example_count"])
        self.assertGreaterEqual(payload["usage_summary"]["non_synthetic"], 1)

    def test_build_payload_fails_when_threshold_is_too_high(self):
        payload = proof_status.build_payload(
            min_live_trials=99,
            min_usage_records=1,
            record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
        )

        self.assertEqual("fail", payload["status"])
        self.assertIn("required >= 99", next(check["detail"] for check in payload["checks"] if check["name"] == "live_task_trials"))

    def test_write_report_outputs_readiness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "PROOF_STATUS.md"
            payload = proof_status.build_payload(
                min_live_trials=8,
                min_usage_records=1,
                record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
            )
            proof_status.write_report(report, payload)

            text = report.read_text(encoding="utf-8")

        self.assertIn("# Proof Status", text)
        self.assertIn("Readiness:", text)
        self.assertIn("checked_in_example_inventory", text)
        self.assertIn("What This Does Not Prove", text)

    def test_main_writes_report_and_returns_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "PROOF_STATUS.md"
            with redirect_stdout(io.StringIO()):
                status = proof_status.main(["--report", report.as_posix()])

            self.assertEqual(0, status)
            self.assertTrue(report.is_file())


if __name__ == "__main__":
    unittest.main()

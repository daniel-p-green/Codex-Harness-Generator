import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


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
    def fake_install_payload(self):
        return {
            "status": "pass",
            "steps": [
                {"name": "profiles", "status": "pass", "profile_count": 20},
                {"name": "init", "status": "pass"},
                {"name": "quickstart", "status": "pass"},
                {"name": "prepare_pilot", "status": "pass"},
                {"name": "init_from_project", "status": "pass"},
                {"name": "validate", "status": "pass"},
                {"name": "inspect", "status": "pass"},
                {"name": "adoption_plan", "status": "pass"},
                {"name": "equivalence", "status": "pass"},
                {"name": "local_eval", "status": "pass"},
                {"name": "public_usage_report", "status": "pass"},
                {"name": "evidence_packet", "status": "pass"},
                {"name": "pilot_pack", "status": "pass"},
                {"name": "usage_from_harness", "status": "pass"},
                {"name": "usage_from_issue_preview", "status": "pass"},
                {"name": "usage_from_issue", "status": "pass"},
                {"name": "prepare_next_pilot", "status": "pass"},
                {"name": "pilot_board", "status": "pass"},
                {"name": "usage_gaps", "status": "pass"},
                {"name": "pilot_campaign", "status": "pass"},
                {"name": "migration_audit", "status": "pass"},
                {"name": "eval", "status": "pass"},
            ],
        }

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
        with patch.object(proof_status, "build_cli_install_payload", return_value=self.fake_install_payload()):
            payload = proof_status.build_payload(
                min_live_trials=8,
                min_usage_records=2,
                record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual(8, payload["task_trials"]["trial_count"])
        self.assertEqual("pass", payload["example_inventory"]["status"])
        self.assertEqual("pass", payload["installable_cli"]["status"])
        install_check = next(check for check in payload["checks"] if check["name"] == "installable_cli")
        self.assertIn("validate=pass", install_check["detail"])
        self.assertIn("quickstart=pass", install_check["detail"])
        self.assertIn("prepare_pilot=pass", install_check["detail"])
        self.assertIn("init_from_project=pass", install_check["detail"])
        self.assertIn("inspect=pass", install_check["detail"])
        self.assertIn("adoption_plan=pass", install_check["detail"])
        self.assertIn("equivalence=pass", install_check["detail"])
        self.assertIn("local_eval=pass", install_check["detail"])
        self.assertIn("public_usage_report=pass", install_check["detail"])
        self.assertIn("evidence_packet=pass", install_check["detail"])
        self.assertIn("pilot_pack=pass", install_check["detail"])
        self.assertIn("usage_from_harness=pass", install_check["detail"])
        self.assertIn("usage_from_issue_preview=pass", install_check["detail"])
        self.assertIn("usage_from_issue=pass", install_check["detail"])
        self.assertIn("prepare_next_pilot=pass", install_check["detail"])
        self.assertIn("pilot_board=pass", install_check["detail"])
        self.assertIn("usage_gaps=pass", install_check["detail"])
        self.assertIn("pilot_campaign=pass", install_check["detail"])
        self.assertIn("migration_audit=pass", install_check["detail"])
        self.assertIn("installable_cli", [check["name"] for check in payload["checks"]])
        self.assertIn("source_freshness_report", [check["name"] for check in payload["checks"]])
        self.assertIn("semantic_alignment_report", [check["name"] for check in payload["checks"]])
        self.assertIn("pilot_board_report", [check["name"] for check in payload["checks"]])
        self.assertEqual(4, payload["example_inventory"]["brief_example_count"])
        self.assertGreaterEqual(payload["usage_summary"]["non_synthetic"], 1)

    def test_status_report_check_requires_markdown_and_json_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = root / "REPORT.md"
            json_report = root / "REPORT.json"
            report.write_text(
                "# Report\n\nGenerated: 2026-06-04T00:00:00Z\nStatus: PASS\n",
                encoding="utf-8",
            )
            json_report.write_text('{"status": "pass"}\n', encoding="utf-8")

            payload = proof_status.check_status_report("report", report, json_report)

            self.assertEqual("pass", payload["status"])
            self.assertIn("generated=2026-06-04T00:00:00Z", payload["detail"])

    def test_status_report_check_fails_when_json_status_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = root / "REPORT.md"
            json_report = root / "REPORT.json"
            report.write_text(
                "# Report\n\nGenerated: 2026-06-04T00:00:00Z\nStatus: PASS\n",
                encoding="utf-8",
            )
            json_report.write_text('{"status": "fail"}\n', encoding="utf-8")

            payload = proof_status.check_status_report("report", report, json_report)

            self.assertEqual("fail", payload["status"])
            self.assertIn("json_status=fail", payload["detail"])

    def test_build_payload_fails_when_threshold_is_too_high(self):
        with patch.object(proof_status, "build_cli_install_payload", return_value=self.fake_install_payload()):
            payload = proof_status.build_payload(
                min_live_trials=99,
                min_usage_records=1,
                record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
            )

        self.assertEqual("fail", payload["status"])
        self.assertIn("required >= 99", next(check["detail"] for check in payload["checks"] if check["name"] == "live_task_trials"))

    def test_build_payload_fails_beta_exit_usage_thresholds_for_current_self_dogfood(self):
        with patch.object(proof_status, "build_cli_install_payload", return_value=self.fake_install_payload()):
            payload = proof_status.build_payload(
                min_live_trials=8,
                min_usage_records=5,
                record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
                min_external_or_multi_project=3,
                min_domains=4,
                min_installed_init_brief=2,
                proof_mode="beta-exit",
            )

        self.assertEqual("fail", payload["status"])
        self.assertEqual("beta-exit", payload["mode"])
        self.assertEqual("Missing beta-exit evidence", payload["readiness"])
        usage_check = next(check for check in payload["checks"] if check["name"] == "non_synthetic_usage")
        self.assertEqual("fail", usage_check["status"])
        self.assertTrue(usage_check["requirement_errors"])

    def test_write_report_outputs_readiness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "PROOF_STATUS.md"
            with patch.object(proof_status, "build_cli_install_payload", return_value=self.fake_install_payload()):
                payload = proof_status.build_payload(
                    min_live_trials=8,
                    min_usage_records=2,
                    record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
                )
            proof_status.write_report(report, payload)

            text = report.read_text(encoding="utf-8")

        self.assertIn("# Proof Status", text)
        self.assertIn("Readiness:", text)
        self.assertIn("Mode:", text)
        self.assertIn("checked_in_example_inventory", text)
        self.assertIn("installable_cli", text)
        self.assertIn("source_freshness_report", text)
        self.assertIn("semantic_alignment_report", text)
        self.assertIn("pilot_board_report", text)
        self.assertIn("What This Does Not Prove", text)

    def test_main_writes_report_and_returns_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "PROOF_STATUS.md"
            with patch.object(proof_status, "build_cli_install_payload", return_value=self.fake_install_payload()):
                with redirect_stdout(io.StringIO()):
                    status = proof_status.main(["--report", report.as_posix()])

            self.assertEqual(0, status)
            self.assertTrue(report.is_file())

    def test_main_beta_exit_applies_roadmap_thresholds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "PROOF_STATUS.md"
            with patch.object(proof_status, "build_cli_install_payload", return_value=self.fake_install_payload()):
                with redirect_stdout(io.StringIO()):
                    status = proof_status.main(["--beta-exit", "--report", report.as_posix()])

            text = report.read_text(encoding="utf-8")

        self.assertEqual(1, status)
        self.assertIn("Mode: beta-exit", text)
        self.assertIn("Readiness: Missing beta-exit evidence", text)
        self.assertIn("requires at least 5", text)


if __name__ == "__main__":
    unittest.main()

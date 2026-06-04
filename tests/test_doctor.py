import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTOR_PATH = REPO_ROOT / "scripts" / "doctor.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("doctor", DOCTOR_PATH)
doctor = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = doctor
spec.loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def write_usage_record(
        self,
        record_dir: Path,
        slug: str,
        domain: str,
        source_type: str = "external",
        generation_path: str = "installed-init-brief",
        evidence_type: str = "private-summary",
    ) -> None:
        payload = {
            "slug": slug,
            "title": f"{slug} usage record",
            "generated": "2026-06-04T12:00:00Z",
            "domain": domain,
            "harness_path": f"/tmp/{slug}",
            "task_summary": "Generated and used a Codex harness for a representative pilot task.",
            "outcome": "success",
            "evidence_type": evidence_type,
            "source_type": source_type,
            "generation_path": generation_path,
            "evidence": [
                "Private reporter summary confirmed the generated harness was used.",
                "The pilot record included a concrete task outcome and verification summary.",
            ],
            "verification": [
                "Reporter-provided verification steps were completed without blocking failures.",
                "The resulting usage record passed the local usage-record validator.",
            ],
            "privacy_review": "Private details were summarized and no secrets or personal data are included.",
            "limitations": ["Evidence is a privacy-preserving summary rather than raw workspace contents."],
        }
        (record_dir / f"{slug}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def fake_install_payload(self):
        return {
            "status": "pass",
            "steps": [
                {"name": "profiles", "status": "pass", "profile_count": 20},
                {"name": "doctor", "status": "pass"},
                {"name": "init", "status": "pass"},
                {"name": "quickstart", "status": "pass"},
                {"name": "prepare_pilot", "status": "pass"},
                {"name": "init_from_project", "status": "pass"},
                {"name": "validate", "status": "pass"},
                {"name": "inspect", "status": "pass"},
                {"name": "adoption_plan", "status": "pass"},
                {"name": "equivalence", "status": "pass"},
                {"name": "upstream_drift", "status": "pass"},
                {"name": "local_eval", "status": "pass"},
                {"name": "public_usage_report", "status": "pass"},
                {"name": "evidence_packet", "status": "pass"},
                {"name": "pilot_pack", "status": "pass"},
                {"name": "usage_from_harness", "status": "pass"},
                {"name": "usage_from_issue_lint", "status": "pass"},
                {"name": "usage_from_issue_preview", "status": "pass"},
                {"name": "usage_from_issue", "status": "pass"},
                {"name": "prepare_next_pilot", "status": "pass"},
                {"name": "prepare_pilot_batch_dry_run", "status": "pass"},
                {"name": "pilot_board", "status": "pass"},
                {"name": "pilot_update", "status": "pass"},
                {"name": "pilot_outreach", "status": "pass"},
                {"name": "pilot_handoff", "status": "pass"},
                {"name": "pilot_handoff_audit", "status": "pass"},
                {"name": "usage_from_issue_pilot_conversion", "status": "pass"},
                {"name": "usage_gaps", "status": "pass"},
                {"name": "beta_exit_audit", "status": "pass"},
                {"name": "beta_status", "status": "pass"},
                {"name": "pilot_campaign", "status": "pass"},
                {"name": "proof_next", "status": "pass"},
                {"name": "migration_audit", "status": "pass"},
                {"name": "prepare_migration", "status": "pass"},
                {"name": "eval", "status": "pass"},
            ],
        }

    def test_required_files_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "present.txt").write_text("ok\n", encoding="utf-8")

            payload = doctor.check_required_files(root, ("present.txt", "missing.txt"))

        self.assertEqual("fail", payload["status"])
        self.assertEqual(["missing.txt"], payload["missing"])
        self.assertEqual("1/2 present", payload["detail"])

    def test_proof_status_report_last_status_is_advisory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "PROOF_STATUS.md"
            report.write_text("# Proof Status\n\nStatus: FAIL\n", encoding="utf-8")

            payload = doctor.check_proof_status_report(report)

        self.assertEqual("pass", payload["status"])
        self.assertIn("last_status=fail", payload["detail"])

    def test_build_payload_passes_for_current_checkout(self):
        payload = doctor.build_payload()

        self.assertEqual("pass", payload["status"], payload)
        self.assertIn("doctor is fast by default", payload["notes"][0])
        self.assertFalse(payload["beta_exit"])
        self.assertIn("codex-harness gate", payload["next_commands"])
        self.assertIn("example_inventory", [check["name"] for check in payload["checks"]])
        self.assertIsNone(payload["installable_cli"])

    def test_beta_exit_mode_applies_external_evidence_thresholds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = doctor.build_payload(record_dir=Path(temp_dir), beta_exit=True)

        self.assertEqual("fail", payload["status"])
        self.assertTrue(payload["beta_exit"])
        self.assertEqual("beta-exit evidence gate needs attention", payload["readiness"])
        self.assertIn("codex-harness proof-status --beta-exit --no-write", payload["next_commands"])
        usage_check = next(check for check in payload["checks"] if check["name"] == "usage_records")
        self.assertEqual("fail", usage_check["status"])
        self.assertIn("records=0/5", usage_check["detail"])
        self.assertIn("external_or_multi_project=0/3", usage_check["detail"])
        self.assertIn("domains=0/4", usage_check["detail"])
        self.assertIn("installed_brief_generation=0/2", usage_check["detail"])
        self.assertTrue(any("external or multi-project" in error for error in usage_check["requirement_errors"]))

    def test_beta_exit_mode_passes_when_evidence_thresholds_are_met(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir)
            self.write_usage_record(record_dir, "external-rag", "RAG apps")
            self.write_usage_record(record_dir, "external-security", "Security audit")
            self.write_usage_record(record_dir, "multi-support", "Customer support", source_type="multi-project")
            self.write_usage_record(
                record_dir,
                "dogfood-api",
                "API design",
                source_type="self-dogfood",
                generation_path="repo-dogfood",
                evidence_type="sanitized",
            )
            self.write_usage_record(
                record_dir,
                "dogfood-evals",
                "Model evals",
                source_type="self-dogfood",
                generation_path="repo-dogfood",
                evidence_type="sanitized",
            )

            payload = doctor.build_payload(record_dir=record_dir, beta_exit=True)

        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["beta_exit"])
        self.assertEqual("beta-exit evidence gate is ready", payload["readiness"])
        usage_check = next(check for check in payload["checks"] if check["name"] == "usage_records")
        self.assertEqual("pass", usage_check["status"])
        self.assertIn("records=5/5", usage_check["detail"])
        self.assertIn("external_or_multi_project=3/3", usage_check["detail"])
        self.assertIn("domains=5/4", usage_check["detail"])
        self.assertIn("installed_brief_generation=3/2", usage_check["detail"])
        self.assertEqual([], usage_check["requirement_errors"])

    def test_include_install_smoke_adds_install_check(self):
        with patch.object(doctor, "build_cli_install_payload", return_value=self.fake_install_payload()):
            payload = doctor.build_payload(include_install_smoke=True)

        self.assertEqual("pass", payload["status"])
        self.assertEqual("pass", payload["installable_cli"]["status"])
        install_check = next(check for check in payload["checks"] if check["name"] == "installable_cli")
        self.assertIn("validate=pass", install_check["detail"])
        self.assertIn("quickstart=pass", install_check["detail"])
        self.assertIn("prepare_pilot=pass", install_check["detail"])
        self.assertIn("init_from_project=pass", install_check["detail"])
        self.assertIn("inspect=pass", install_check["detail"])
        self.assertIn("adoption_plan=pass", install_check["detail"])
        self.assertIn("equivalence=pass", install_check["detail"])
        self.assertIn("upstream_drift=pass", install_check["detail"])
        self.assertIn("local_eval=pass", install_check["detail"])
        self.assertIn("public_usage_report=pass", install_check["detail"])
        self.assertIn("evidence_packet=pass", install_check["detail"])
        self.assertIn("pilot_pack=pass", install_check["detail"])
        self.assertIn("usage_from_harness=pass", install_check["detail"])
        self.assertIn("usage_from_issue_lint=pass", install_check["detail"])
        self.assertIn("usage_from_issue_preview=pass", install_check["detail"])
        self.assertIn("usage_from_issue=pass", install_check["detail"])
        self.assertIn("prepare_next_pilot=pass", install_check["detail"])
        self.assertIn("prepare_pilot_batch=pass", install_check["detail"])
        self.assertIn("pilot_board=pass", install_check["detail"])
        self.assertIn("pilot_update=pass", install_check["detail"])
        self.assertIn("pilot_outreach=pass", install_check["detail"])
        self.assertIn("pilot_handoff=pass", install_check["detail"])
        self.assertIn("pilot_handoff_audit=pass", install_check["detail"])
        self.assertIn("usage_from_issue_pilot_conversion=pass", install_check["detail"])
        self.assertIn("usage_gaps=pass", install_check["detail"])
        self.assertIn("beta_exit_audit=pass", install_check["detail"])
        self.assertIn("beta_status=pass", install_check["detail"])
        self.assertIn("pilot_campaign=pass", install_check["detail"])
        self.assertIn("proof_next=pass", install_check["detail"])
        self.assertIn("migration_audit=pass", install_check["detail"])
        self.assertIn("prepare_migration=pass", install_check["detail"])
        self.assertIn("installable_cli", [check["name"] for check in payload["checks"]])

    def test_main_json_returns_failure_for_unmet_usage_threshold(self):
        output = io.StringIO()

        with redirect_stdout(output):
            status = doctor.main(["--min-usage-records", "999", "--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(1, status)
        self.assertEqual("fail", payload["status"])
        usage_check = next(check for check in payload["checks"] if check["name"] == "usage_records")
        self.assertEqual("fail", usage_check["status"])
        self.assertTrue(usage_check["requirement_errors"])

    def test_main_beta_exit_json_returns_failure_for_missing_external_evidence(self):
        output = io.StringIO()

        with tempfile.TemporaryDirectory() as temp_dir:
            with redirect_stdout(output):
                status = doctor.main(["--record-dir", temp_dir, "--beta-exit", "--json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(1, status)
        self.assertEqual("fail", payload["status"])
        self.assertTrue(payload["beta_exit"])
        self.assertIn("usage-gaps --no-write", " ".join(payload["next_commands"]))

    def test_text_output_includes_next_commands(self):
        output = io.StringIO()

        with redirect_stdout(output):
            status = doctor.main([])

        text = output.getvalue()
        self.assertEqual(0, status)
        self.assertIn("Codex Harness Doctor: PASS", text)
        self.assertIn("codex-harness init", text)


if __name__ == "__main__":
    unittest.main()

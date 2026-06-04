import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "beta_exit_audit.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("beta_exit_audit", SCRIPT)
beta_exit_audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = beta_exit_audit
spec.loader.exec_module(beta_exit_audit)


class BetaExitAuditTests(unittest.TestCase):
    def valid_record(self, slug: str, domain: str, source_type: str, generation_path: str) -> dict:
        return {
            "slug": slug,
            "title": slug.replace("-", " ").title(),
            "generated": "2026-06-04T12:00:00Z",
            "domain": domain,
            "harness_path": f"public-harness/{slug}",
            "task_summary": "Used a generated harness on a privacy-safe pilot task.",
            "outcome": "success",
            "evidence_type": "sanitized",
            "source_type": source_type,
            "generation_path": generation_path,
            "evidence": ["public-safe artifact reviewed", "local eval report passed"],
            "verification": ["task trial recorded", "privacy review completed"],
            "privacy_review": "Public-safe summary only; no secrets, personal data, private paths, proprietary source, or raw logs.",
            "limitations": ["Single pilot task."],
        }

    def write_record(self, root: Path, payload: dict) -> None:
        (root / f"{payload['slug']}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_ready_records(self, root: Path) -> None:
        records = [
            ("external-llm-app", "LLM app", "external", "installed-init-brief"),
            ("multi-project-docs", "Documentation", "multi-project", "installed-quickstart"),
            ("external-data-tool", "Data tooling", "external", "installed-init-from-project"),
            ("self-dogfood-cli", "CLI tooling", "self-dogfood", "manual-migration"),
            ("self-dogfood-evals", "Evaluation", "self-dogfood", "repo-dogfood"),
        ]
        for slug, domain, source_type, generation_path in records:
            self.write_record(root, self.valid_record(slug, domain, source_type, generation_path))

    def test_build_payload_reports_missing_current_beta_exit_evidence(self):
        payload = beta_exit_audit.build_payload(
            REPO_ROOT / "Docs" / "Environment" / "usage-records",
            pilot_record_dir=REPO_ROOT / "Docs" / "Environment" / "pilot-records",
            usage_record_dir=REPO_ROOT / "Docs" / "Environment" / "usage-records",
        )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("missing-beta-exit-evidence", payload["readiness"])
        self.assertFalse(payload["beta_exit_ready"])
        self.assertTrue(any(item["status"] == "missing" for item in payload["criteria"]))
        self.assertIn("does not itself prove external adoption", payload["claim_boundary"])

    def test_build_payload_marks_ready_when_usage_thresholds_are_satisfied(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "usage-records"
            pilot_record_dir = root / "pilot-records"
            record_dir.mkdir()
            pilot_record_dir.mkdir()
            self.write_ready_records(record_dir)

            payload = beta_exit_audit.build_payload(
                record_dir,
                pilot_record_dir=pilot_record_dir,
                usage_record_dir=record_dir,
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("beta-exit-ready-for-final-gate", payload["readiness"])
        self.assertTrue(payload["beta_exit_ready"])
        self.assertEqual("pass", next(item["status"] for item in payload["criteria"] if item["name"] == "external_or_multi_project_records"))

    def test_write_report_includes_criteria_and_next_actions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "usage-records"
            pilot_record_dir = root / "pilot-records"
            record_dir.mkdir()
            pilot_record_dir.mkdir()
            self.write_record(record_dir, self.valid_record("self-dogfood-docs", "Documentation", "self-dogfood", "repo-dogfood"))
            payload = beta_exit_audit.build_payload(record_dir, pilot_record_dir=pilot_record_dir, usage_record_dir=record_dir)
            report = root / "BETA_EXIT_AUDIT.md"

            beta_exit_audit.write_report(report, payload)
            text = report.read_text(encoding="utf-8")

        self.assertIn("# Beta Exit Audit", text)
        self.assertIn("## Criteria", text)
        self.assertIn("external_or_multi_project_records", text)
        self.assertIn("## Next Actions", text)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
USAGE_GAPS_PATH = REPO_ROOT / "scripts" / "usage_gaps.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("usage_gaps", USAGE_GAPS_PATH)
usage_gaps = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = usage_gaps
spec.loader.exec_module(usage_gaps)


class UsageGapsTests(unittest.TestCase):
    def valid_payload(self, slug: str = "external-llm-app") -> dict:
        return {
            "slug": slug,
            "title": slug.replace("-", " ").title(),
            "generated": "2026-06-04T12:00:00Z",
            "domain": "LLM app",
            "harness_path": f"examples/live-create/{slug}",
            "task_summary": "Used a generated harness on a privacy-safe pilot task.",
            "outcome": "success",
            "evidence_type": "private-summary",
            "source_type": "external",
            "generation_path": "installed-init-brief",
            "evidence": ["private summary reviewed", "sanitized artifact checklist completed"],
            "verification": ["expected artifact exists", "privacy scan passed"],
            "privacy_review": "Public-safe summary only; raw project files are private.",
            "limitations": ["Single pilot task."],
        }

    def write_payload(self, root: Path, payload: dict) -> None:
        (root / f"{payload['slug']}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_build_payload_reports_remaining_beta_exit_gaps(self):
        payload = self.valid_payload("self-dogfood-docs")
        payload["source_type"] = "self-dogfood"
        payload["domain"] = "Documentation"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, payload)

            result = usage_gaps.build_payload(root)

        self.assertEqual("pass", result["status"], result)
        self.assertEqual("missing-beta-exit-evidence", result["readiness"])
        self.assertEqual(4, result["gaps"]["records"])
        self.assertEqual(3, result["gaps"]["external_or_multi_project"])
        self.assertEqual(3, result["gaps"]["domains"])
        self.assertEqual(1, result["gaps"]["installed_init_brief"])
        self.assertTrue(any("external or multi-project" in item for item in result["recommendations"]))
        self.assertEqual(4, len(result["suggested_pilots"]))
        self.assertEqual("llm-app", result["suggested_pilots"][0]["profile"])
        self.assertEqual("external", result["suggested_pilots"][0]["source_type"])
        self.assertEqual("installed-quickstart", result["suggested_pilots"][0]["generation_path"])
        self.assertIn("codex-harness prepare-pilot", result["suggested_pilots"][0]["commands"][0])
        self.assertIn("--domain \"LLM app\"", result["suggested_pilots"][0]["commands"][0])

    def test_build_payload_marks_ready_when_targets_are_satisfied(self):
        records = []
        for index, (slug, domain, source_type, generation_path) in enumerate(
            [
                ("external-llm-app", "LLM app", "external", "installed-init-brief"),
                ("multi-project-docs", "Documentation", "multi-project", "installed-quickstart"),
                ("external-data-tool", "Data tooling", "external", "installed-init-from-project"),
                ("self-dogfood-cli", "CLI tooling", "self-dogfood", "manual-migration"),
                ("self-dogfood-evals", "Evaluation", "self-dogfood", "repo-dogfood"),
            ]
        ):
            payload = self.valid_payload(slug)
            payload["domain"] = domain
            payload["source_type"] = source_type
            payload["generation_path"] = generation_path
            payload["generated"] = f"2026-06-04T12:0{index}:00Z"
            records.append(payload)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for payload in records:
                self.write_payload(root, payload)

            result = usage_gaps.build_payload(root)

        self.assertEqual("pass", result["status"], result)
        self.assertEqual("beta-exit-evidence-ready", result["readiness"])
        self.assertFalse(any(result["gaps"].values()))
        self.assertIn("Beta-exit usage thresholds are satisfied", result["recommendations"][0])
        self.assertEqual([], result["suggested_pilots"])

    def test_write_report_includes_gap_sections(self):
        payload = self.valid_payload("self-dogfood-docs")
        payload["source_type"] = "self-dogfood"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, payload)
            result = usage_gaps.build_payload(root)
            report = root / "USAGE_GAPS.md"

            usage_gaps.write_report(report, result)

            text = report.read_text(encoding="utf-8")

        self.assertIn("# Usage Evidence Gaps", text)
        self.assertIn("## Remaining Gaps", text)
        self.assertIn("- External or multi-project records: 3", text)
        self.assertIn("## Suggested Pilot Targets", text)
        self.assertIn("codex-harness prepare-pilot", text)
        self.assertIn("## Recommended Next Moves", text)

    def test_build_payload_fails_when_records_are_only_synthetic(self):
        payload = self.valid_payload("synthetic-task")
        payload["evidence_type"] = "synthetic"
        payload["source_type"] = "self-dogfood"
        payload["evidence"] = ["synthetic report generated"]
        payload["verification"] = ["expected terms found"]
        payload["limitations"] = ["Synthetic task only."]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, payload)

            result = usage_gaps.build_payload(root)

        self.assertEqual("fail", result["status"])
        self.assertEqual("missing-beta-exit-evidence", result["readiness"])
        self.assertTrue(result["validation"]["requirement_errors"])


if __name__ == "__main__":
    unittest.main()

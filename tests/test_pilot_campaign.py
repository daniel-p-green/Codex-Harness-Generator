import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_pilot_campaign.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_pilot_campaign", SCRIPT)
export_pilot_campaign = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_pilot_campaign
spec.loader.exec_module(export_pilot_campaign)


class PilotCampaignTests(unittest.TestCase):
    def valid_payload(self, slug: str = "self-dogfood-docs") -> dict:
        return {
            "slug": slug,
            "title": slug.replace("-", " ").title(),
            "generated": "2026-06-04T12:00:00Z",
            "domain": "Documentation",
            "harness_path": f"examples/live-create/{slug}",
            "task_summary": "Used a generated harness on a privacy-safe pilot task.",
            "outcome": "success",
            "evidence_type": "private-summary",
            "source_type": "self-dogfood",
            "generation_path": "repo-dogfood",
            "evidence": ["private summary reviewed", "sanitized artifact checklist completed"],
            "verification": ["expected artifact exists", "privacy scan passed"],
            "privacy_review": "Public-safe summary only; raw project files are private.",
            "limitations": ["Single pilot task."],
        }

    def write_payload(self, root: Path, payload: dict) -> None:
        (root / f"{payload['slug']}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def test_build_payload_turns_gaps_into_pilot_slots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, self.valid_payload())

            result = export_pilot_campaign.build_payload(root, max_pilots=2)

        self.assertEqual("pass", result["status"], result)
        self.assertEqual("missing-beta-exit-evidence", result["readiness"])
        self.assertEqual(2, result["pilot_count"])
        self.assertEqual("llm-app", result["pilots"][0]["profile"])
        self.assertEqual("installed-quickstart", result["pilots"][0]["generation_path"])

    def test_write_report_includes_privacy_and_claim_boundaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, self.valid_payload())
            result = export_pilot_campaign.build_payload(root, max_pilots=1)
            report = root / "PILOT_CAMPAIGN.md"

            export_pilot_campaign.write_report(report, result)

            text = report.read_text(encoding="utf-8")

        self.assertIn("# External Pilot Campaign", text)
        self.assertIn("## Pilot Slots", text)
        self.assertIn("codex-harness prepare-next-pilot", text)
        self.assertIn("codex-harness prepare-pilot", text)
        self.assertIn("Reporter evidence checklist", text)
        self.assertIn("Do not drop the beta label", text)
        self.assertIn("They do not prove broad external adoption", text)

    def test_ready_payload_has_no_pilots(self):
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

            result = export_pilot_campaign.build_payload(root)

        self.assertEqual("beta-exit-evidence-ready", result["readiness"])
        self.assertEqual(0, result["pilot_count"])
        self.assertEqual([], result["pilots"])


if __name__ == "__main__":
    unittest.main()

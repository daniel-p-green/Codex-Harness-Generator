import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_pilot_outreach.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_pilot_outreach", SCRIPT)
export_pilot_outreach = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_pilot_outreach
spec.loader.exec_module(export_pilot_outreach)

import pilot_board


class PilotOutreachTests(unittest.TestCase):
    def pilot_payload(self, slug: str = "llm-app-pilot", domain: str = "LLM app") -> dict:
        return {
            "generated": "2026-06-04T12:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": slug,
                "title": slug.replace("-", " "),
                "domain": domain,
                "profile": "llm-app",
                "source_type": "external",
                "generation_path": "installed-quickstart",
                "project_name": "LLM App Workspace Pilot",
            },
            "prepared_pilot": {
                "target": "/tmp/codex-llm-app-pilot",
                "pilot_pack": {
                    "harness_label": "LLM App Workspace Pilot",
                    "pack": "Docs/Environment/LLM_APP_PILOT_PACK.md",
                    "issue_draft": "Docs/Environment/LLM_APP_USAGE_ISSUE_DRAFT.md",
                },
            },
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
        }

    def args(self, root: Path, **overrides) -> Namespace:
        values = {
            "record_dir": (root / "pilot-records").as_posix(),
            "usage_record_dir": (root / "usage-records").as_posix(),
            "usage_report": "Docs/Environment/USAGE_RECORDS.md",
            "pilot_board_report": "Docs/Environment/PILOT_BOARD.md",
            "out": (root / "PILOT_OUTREACH.md").as_posix(),
            "status": None,
            "slug": None,
        }
        values.update(overrides)
        return Namespace(**values)

    def write_pilot_record(self, root: Path, status: str = "prepared", slug: str = "llm-app-pilot") -> None:
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        record = pilot_board.build_record(self.pilot_payload(slug=slug), status=status)
        (record_dir / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def test_build_payload_exports_prepared_pilot_outreach(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = export_pilot_outreach.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("outreach-ready", payload["readiness"])
        self.assertEqual(1, payload["outreach_count"])
        record = payload["records"][0]
        self.assertEqual("llm-app-pilot", record["slug"])
        self.assertIn("Would you be willing", record["reporter_message"])
        self.assertIn("Do not include secrets", record["reporter_message"])
        self.assertIn("pilot-update llm-app-pilot --status invited", record["commands"]["mark_invited"])
        self.assertIn("usage-from-issue <completed-issue.md>", record["commands"]["convert_issue"])
        self.assertIn("usage-from-harness <generated-harness> --slug llm-app-pilot", record["commands"]["preview_harness"])
        self.assertIn("not usage proof", payload["claim_boundary"])

    def test_write_report_outputs_reporter_message_and_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = export_pilot_outreach.build_payload(args)

            export_pilot_outreach.write_report(Path(args.out), payload)

            text = Path(args.out).read_text(encoding="utf-8")

        self.assertIn("# Pilot Outreach Packet", text)
        self.assertIn("Reporter message:", text)
        self.assertIn("Maintainer tracking:", text)
        self.assertIn("Issue-body conversion:", text)
        self.assertIn("Copied-harness conversion:", text)
        self.assertIn("Sending or tracking an invite is not adoption evidence", text)

    def test_status_filter_can_find_completed_pilots_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root, status="prepared", slug="prepared-pilot")
            self.write_pilot_record(root, status="completed", slug="completed-pilot")

            payload = export_pilot_outreach.build_payload(self.args(root, status=["completed"]))

        self.assertEqual(1, payload["outreach_count"])
        self.assertEqual("completed-pilot", payload["records"][0]["slug"])

    def test_no_active_pilots_is_still_a_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pilot-records").mkdir()

            payload = export_pilot_outreach.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"])
        self.assertEqual("no-active-pilots", payload["readiness"])
        self.assertEqual(0, payload["outreach_count"])


if __name__ == "__main__":
    unittest.main()

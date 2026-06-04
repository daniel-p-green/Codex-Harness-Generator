import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "pilot_board.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("pilot_board", SCRIPT)
pilot_board = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = pilot_board
spec.loader.exec_module(pilot_board)


class PilotBoardTests(unittest.TestCase):
    def pilot_payload(self):
        return {
            "generated": "2026-06-04T12:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": "llm-app-pilot",
                "title": "LLM app pilot",
                "domain": "LLM app",
                "profile": "llm-app",
                "source_type": "external",
                "generation_path": "installed-quickstart",
                "project_name": "LLM App Workspace Pilot",
            },
            "prepared_pilot": {
                "target": "/tmp/codex-llm-app-pilot",
                "pilot_pack": {
                    "harness_label": "LLM App Workspace Pilot",
                    "pack": "/tmp/PILOT_PACK.md",
                    "issue_draft": "/tmp/ISSUE.md",
                },
            },
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
        }

    def test_build_record_from_prepared_pilot_payload(self):
        record = pilot_board.build_record(self.pilot_payload(), notes="sent to reporter")

        self.assertEqual("llm-app-pilot", record["slug"])
        self.assertEqual("prepared", record["status"])
        self.assertEqual("LLM app", record["domain"])
        self.assertEqual("installed-quickstart", record["generation_path"])
        self.assertIn("not usage proof", record["claim_boundary"])

    def test_build_payload_summarizes_pending_pilots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir)
            record = pilot_board.build_record(self.pilot_payload())
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            payload = pilot_board.build_payload(record_dir)

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("pilot-funnel-active", payload["readiness"])
        self.assertEqual(1, payload["summary"]["pending"])
        self.assertEqual(1, payload["summary"]["external_or_multi_project"])
        self.assertEqual(1, payload["summary"]["installed_brief_generation"])
        self.assertEqual(1, payload["summary"]["distinct_domains"])
        self.assertIn("not usage proof", payload["claim_boundary"])

    def test_converted_pilot_requires_usage_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir)
            record = pilot_board.build_record(self.pilot_payload(), status="converted")
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            payload = pilot_board.build_payload(record_dir)

        self.assertEqual("fail", payload["status"])
        self.assertTrue(any("usage_record" in error for error in payload["errors"]))

    def test_write_report_outputs_board_boundary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            record_dir.mkdir()
            record = pilot_board.build_record(self.pilot_payload())
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")
            report = root / "PILOT_BOARD.md"
            payload = pilot_board.build_payload(record_dir)

            pilot_board.write_report(report, payload)
            text = report.read_text(encoding="utf-8")

        self.assertIn("# Pilot Board", text)
        self.assertIn("LLM app", text)
        self.assertIn("not usage proof", text)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_pilot_reporter_replies.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_pilot_reporter_replies", SCRIPT)
export_pilot_reporter_replies = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_pilot_reporter_replies
spec.loader.exec_module(export_pilot_reporter_replies)

import pilot_board


class PilotReporterRepliesTests(unittest.TestCase):
    def pilot_payload(self, slug: str = "llm-app-pilot") -> dict:
        return {
            "generated": "2026-06-04T12:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": slug,
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
            "out_dir": (root / "pilot-reporter-replies").as_posix(),
            "report": (root / "PILOT_REPORTER_REPLIES.md").as_posix(),
            "status": None,
            "slug": None,
        }
        values.update(overrides)
        return Namespace(**values)

    def write_pilot_record(self, root: Path, status: str = "invited") -> None:
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        record = pilot_board.build_record(self.pilot_payload(), status=status)
        notes = "opened public pilot issue https://github.com/example/repo/issues/42"
        record["notes"] = notes
        record["status_history"] = [{"notes": notes}]
        (record_dir / "llm-app-pilot.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def test_build_payload_writes_importer_shaped_reply_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = export_pilot_reporter_replies.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("reporter-replies-ready", payload["readiness"])
        self.assertEqual(1, payload["reply_count"])
        record = payload["records"][0]
        self.assertEqual("https://github.com/example/repo/issues/42", record["issue_url"])
        self.assertIn("### Outcome", record["reply_template"])
        self.assertIn("### Evidence", record["reply_template"])
        self.assertIn("usage-from-github-issue https://github.com/example/repo/issues/42", record["preview_github_issue"])
        for field in ("outcome", "task_summary", "evidence", "verification", "privacy_review", "limitations"):
            self.assertIn(field, record["section_names"])

    def test_write_outputs_creates_reply_file_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = export_pilot_reporter_replies.build_payload(args)

            export_pilot_reporter_replies.write_outputs(payload)

            reply = root / "pilot-reporter-replies" / "llm-app-pilot-reporter-reply.md"
            report = root / "PILOT_REPORTER_REPLIES.md"
            reply_text = reply.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")

        self.assertIn("# Reporter Completion Reply: llm-app-pilot", reply_text)
        self.assertIn("Copy the Markdown below into a new GitHub issue comment", reply_text)
        self.assertIn("This reply is not usage proof", reply_text)
        self.assertIn("# Pilot Reporter Replies", report_text)
        self.assertIn("Reporter reply templates: 1", report_text)
        self.assertIn("Do not count generated reply templates as usage evidence", report_text)

    def test_no_active_pilots_is_still_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pilot-records").mkdir()

            payload = export_pilot_reporter_replies.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"])
        self.assertEqual("no-active-pilots", payload["readiness"])
        self.assertEqual(0, payload["reply_count"])


if __name__ == "__main__":
    unittest.main()

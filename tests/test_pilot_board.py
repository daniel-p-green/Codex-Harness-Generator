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

    def usage_record(self, slug: str = "llm-app-pilot") -> dict:
        return {
            "slug": slug,
            "title": "LLM app pilot",
            "generated": "2026-06-04T14:00:00Z",
            "domain": "LLM app",
            "harness_path": "public pilot harness",
            "task_summary": "Reporter completed one privacy-safe LLM app pilot task.",
            "outcome": "success",
            "evidence_type": "sanitized",
            "source_type": "external",
            "generation_path": "installed-quickstart",
            "evidence": ["public-safe artifact reviewed", "local eval report passed"],
            "verification": ["task trial recorded", "privacy review completed"],
            "privacy_review": "Public-safe summary only; no secrets, personal data, private paths, proprietary source, or raw logs.",
            "limitations": ["Single external pilot task."],
        }

    def write_usage_record(self, root: Path, payload: dict | None = None) -> Path:
        record = payload or self.usage_record()
        path = root / f"{record['slug']}.json"
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return path

    def test_build_record_from_prepared_pilot_payload(self):
        record = pilot_board.build_record(self.pilot_payload(), notes="sent to reporter")

        self.assertEqual("llm-app-pilot", record["slug"])
        self.assertEqual("prepared", record["status"])
        self.assertEqual("LLM app", record["domain"])
        self.assertEqual("installed-quickstart", record["generation_path"])
        self.assertEqual("generated pilot harness: llm-app-pilot", record["target"])
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

    def test_build_payload_rejects_local_target_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir)
            record = pilot_board.build_record(self.pilot_payload())
            record["target"] = "/private/tmp/codex-llm-app-pilot"
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            payload = pilot_board.build_payload(record_dir)

        self.assertEqual("fail", payload["status"])
        self.assertTrue(any("target must be public-safe" in error for error in payload["errors"]))

    def test_update_record_file_moves_pilot_through_funnel(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir)
            record = pilot_board.build_record(self.pilot_payload())
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            update = pilot_board.update_record_file(
                record_dir,
                "llm-app-pilot",
                "invited",
                notes="sent to reporter",
                updated="2026-06-04T13:30:00Z",
            )
            payload = pilot_board.build_payload(record_dir)
            updated_record = payload["records"][0]

        self.assertEqual("pass", update["status"])
        self.assertEqual("invited", updated_record["status"])
        self.assertEqual("sent to reporter", updated_record["notes"])
        self.assertEqual("pilot-funnel-active", payload["readiness"])
        self.assertEqual(
            {
                "at": "2026-06-04T13:30:00Z",
                "from": "prepared",
                "to": "invited",
                "notes": "sent to reporter",
                "usage_record": "",
            },
            updated_record["status_history"][0],
        )

    def test_update_record_file_requires_usage_record_when_converted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir)
            record = pilot_board.build_record(self.pilot_payload())
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                pilot_board.update_record_file(record_dir, "llm-app-pilot", "converted")

    def test_update_record_file_allows_converted_with_valid_usage_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "pilot-records"
            usage_record_dir = root / "usage-records"
            record_dir.mkdir()
            usage_record_dir.mkdir()
            self.write_usage_record(usage_record_dir)
            record = pilot_board.build_record(self.pilot_payload(), status="completed")
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            pilot_board.update_record_file(
                record_dir,
                "llm-app-pilot",
                "converted",
                usage_record="llm-app-pilot",
                updated="2026-06-04T14:00:00Z",
                usage_record_dir=usage_record_dir,
            )
            payload = pilot_board.build_payload(record_dir, usage_record_dir=usage_record_dir)
            updated_record = payload["records"][0]

        self.assertEqual("pass", payload["status"])
        self.assertEqual("pilot-funnel-clear", payload["readiness"])
        self.assertEqual(1, payload["summary"]["converted_validated"])
        self.assertEqual("converted", updated_record["status"])
        self.assertEqual("llm-app-pilot", updated_record["usage_record"])
        self.assertIn("llm-app-pilot.json", updated_record["_validated_usage_record"])

    def test_build_payload_fails_converted_pilot_with_missing_usage_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "pilot-records"
            usage_record_dir = root / "usage-records"
            record_dir.mkdir()
            usage_record_dir.mkdir()
            record = pilot_board.build_record(self.pilot_payload(), status="converted")
            record["usage_record"] = "missing-usage"
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            payload = pilot_board.build_payload(record_dir, usage_record_dir=usage_record_dir)

        self.assertEqual("fail", payload["status"])
        self.assertTrue(any("usage_record not found" in error for error in payload["errors"]))

    def test_build_payload_fails_converted_pilot_with_mismatched_usage_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "pilot-records"
            usage_record_dir = root / "usage-records"
            record_dir.mkdir()
            usage_record_dir.mkdir()
            usage = self.usage_record()
            usage["domain"] = "security audit"
            self.write_usage_record(usage_record_dir, usage)
            record = pilot_board.build_record(self.pilot_payload(), status="converted")
            record["usage_record"] = "llm-app-pilot"
            (record_dir / "llm-app-pilot.json").write_text(json.dumps(record) + "\n", encoding="utf-8")

            payload = pilot_board.build_payload(record_dir, usage_record_dir=usage_record_dir)

        self.assertEqual("fail", payload["status"])
        self.assertTrue(any("domain mismatch" in error for error in payload["errors"]))

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

import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "prepare_pilot.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("prepare_pilot", SCRIPT)
prepare_pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = prepare_pilot
spec.loader.exec_module(prepare_pilot)


class PreparePilotTests(unittest.TestCase):
    def test_prepare_pilot_generates_harness_pack_and_issue_draft(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            target = temp_path / "pilot"
            pack_out = temp_path / "PILOT_PACK.md"
            issue_out = temp_path / "ISSUE_DRAFT.md"
            args = Namespace(
                target=target.as_posix(),
                brief="RAG app with prompts, evals, and retrieval checks",
                project_name="External RAG Pilot Harness",
                notes="external pilot test",
                generated_date="2026-06-04",
                created="2026-06-04T12:00:00Z",
                generated="2026-06-04T12:00:00Z",
                target_label="external-rag-pilot",
                limit=3,
                allow_low_confidence=False,
                force=False,
                min_score=90,
                min_successes=1,
                domain="LLM app",
                slug="external-rag-pilot",
                title="External RAG pilot",
                source_type="external",
                generation_path="installed-quickstart",
                harness_label="external RAG pilot harness",
                out=pack_out.as_posix(),
                issue_out=issue_out.as_posix(),
                pilot_record_dir=None,
                pilot_record_out=None,
                pilot_status="prepared",
                pilot_notes="",
            )

            payload = prepare_pilot.build_payload(args)
            pack = pack_out.read_text(encoding="utf-8")
            issue = issue_out.read_text(encoding="utf-8")
            quickstart_report = target / "Docs" / "Environment" / "QUICKSTART_REPORT.md"
            quickstart_report_exists = quickstart_report.is_file()

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("llm-app", payload["profile"])
        self.assertEqual("pass", payload["quickstart"]["status"])
        self.assertEqual("pass", payload["pilot_pack"]["status"])
        self.assertTrue(quickstart_report_exists)
        self.assertIn("# External Pilot Pack", pack)
        self.assertIn("external RAG pilot harness", pack)
        self.assertIn("### Domain or project type", issue)
        self.assertIn("LLM app", issue)
        self.assertIsNone(payload["pilot_record"])
        self.assertIn("Prepared pilot materials are not usage proof", payload["claim_boundary"])

    def test_prepare_pilot_can_write_pilot_board_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            target = temp_path / "pilot"
            pilot_records = temp_path / "pilot-records"
            args = Namespace(
                target=target.as_posix(),
                brief="RAG app with prompts, evals, and retrieval checks",
                project_name="External RAG Pilot Harness",
                notes="external pilot test",
                generated_date="2026-06-04",
                created="2026-06-04T12:00:00Z",
                generated="2026-06-04T12:00:00Z",
                target_label="external-rag-pilot",
                limit=3,
                allow_low_confidence=False,
                force=False,
                min_score=90,
                min_successes=1,
                domain="LLM app",
                slug="external-rag-pilot",
                title="External RAG pilot",
                source_type="external",
                generation_path="installed-quickstart",
                harness_label="external RAG pilot harness",
                out=(temp_path / "PILOT_PACK.md").as_posix(),
                issue_out=(temp_path / "ISSUE_DRAFT.md").as_posix(),
                pilot_record_dir=pilot_records.as_posix(),
                pilot_record_out=None,
                pilot_status="prepared",
                pilot_notes="prepared for reporter",
            )

            payload = prepare_pilot.build_payload(args)
            record_path = Path(payload["pilot_record"]["path"])
            record = json.loads(record_path.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("pass", payload["pilot_record"]["status"])
        self.assertEqual("external-rag-pilot", record["slug"])
        self.assertEqual("prepared", record["status"])
        self.assertEqual("prepared for reporter", record["notes"])
        self.assertEqual("external RAG pilot harness", record["harness_label"])
        self.assertEqual("generated pilot harness: external-rag-pilot", record["target"])


if __name__ == "__main__":
    unittest.main()

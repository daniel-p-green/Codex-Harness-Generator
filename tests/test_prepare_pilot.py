import importlib.util
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
        self.assertIn("Prepared pilot materials are not usage proof", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()

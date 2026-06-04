import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "prepare_next_pilot.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("prepare_next_pilot", SCRIPT)
prepare_next_pilot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = prepare_next_pilot
spec.loader.exec_module(prepare_next_pilot)


class PrepareNextPilotTests(unittest.TestCase):
    def write_record(self, root: Path) -> None:
        payload = {
            "slug": "self-dogfood-docs",
            "title": "Self Dogfood Docs",
            "generated": "2026-06-04T12:00:00Z",
            "domain": "Documentation",
            "harness_path": "examples/live-create/self-dogfood-docs",
            "task_summary": "Used a generated harness on a privacy-safe docs task.",
            "outcome": "success",
            "evidence_type": "private-summary",
            "source_type": "self-dogfood",
            "generation_path": "installed-init-brief",
            "evidence": ["private summary reviewed", "sanitized artifact checklist completed"],
            "verification": ["expected artifact exists", "privacy scan passed"],
            "privacy_review": "Public-safe summary only; raw project files are private.",
            "limitations": ["Single pilot task."],
        }
        (root / f"{payload['slug']}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def args(self, record_dir: Path, target: Path, pack_out: Path, issue_out: Path, index: int = 1) -> Namespace:
        return Namespace(
            target=target.as_posix(),
            record_dir=record_dir.as_posix(),
            index=index,
            brief=None,
            project_name=None,
            notes="next pilot test",
            domain=None,
            slug=None,
            title=None,
            source_type=None,
            generation_path=None,
            harness_label=None,
            out=pack_out.as_posix(),
            issue_out=issue_out.as_posix(),
            min_successes=1,
            min_score=90,
            target_label="next-pilot-target",
            limit=3,
            allow_low_confidence=False,
            generated_date="2026-06-04",
            created="2026-06-04T12:00:00Z",
            generated="2026-06-04T12:00:00Z",
            min_records=5,
            min_external_or_multi_project=3,
            min_domains=4,
            min_installed_init_brief=2,
            pilot_record_dir=None,
            pilot_record_out=None,
            pilot_status="prepared",
            pilot_notes="",
            force=False,
        )

    def test_prepare_next_pilot_uses_first_usage_gap_suggestion(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            record_dir.mkdir()
            self.write_record(record_dir)
            target = root / "pilot"
            pack_out = root / "PILOT_PACK.md"
            issue_out = root / "ISSUE.md"

            payload = prepare_next_pilot.build_payload(self.args(record_dir, target, pack_out, issue_out))

            pack = pack_out.read_text(encoding="utf-8")
            issue = issue_out.read_text(encoding="utf-8")

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual(1, payload["selected_index"])
        self.assertEqual("llm-app", payload["selected_pilot"]["profile"])
        self.assertEqual("LLM app", payload["selected_pilot"]["domain"])
        self.assertEqual("pass", payload["prepared_pilot"]["status"])
        self.assertEqual("llm-app", payload["prepared_pilot"]["profile"])
        self.assertIn("# External Pilot Pack", pack)
        self.assertIn("LLM App Workspace Pilot", pack)
        self.assertIn("### Domain or project type", issue)
        self.assertIn("LLM app", issue)
        self.assertIn("not usage proof", payload["claim_boundary"])
        self.assertIsNone(payload["pilot_record"])

    def test_prepare_next_pilot_can_write_pilot_board_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            record_dir.mkdir()
            self.write_record(record_dir)
            target = root / "pilot"
            pack_out = root / "PILOT_PACK.md"
            issue_out = root / "ISSUE.md"
            pilot_records = root / "pilot-records"
            args = self.args(record_dir, target, pack_out, issue_out)
            args.pilot_record_dir = pilot_records.as_posix()
            args.pilot_notes = "prepared for external reporter"

            payload = prepare_next_pilot.build_payload(args)
            record_path = Path(payload["pilot_record"]["path"])
            record = json.loads(record_path.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("pass", payload["pilot_record"]["status"])
        self.assertEqual("llm-app-pilot", record["slug"])
        self.assertEqual("prepared", record["status"])
        self.assertEqual("generated pilot harness: llm-app-pilot", record["target"])
        self.assertEqual("prepared for external reporter", record["notes"])

    def test_select_pilot_rejects_out_of_range_index(self):
        payload = {"suggested_pilots": [{"profile": "llm-app"}]}

        with self.assertRaises(SystemExit):
            prepare_next_pilot.select_pilot(payload, 2)


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "prepare_pilot_batch.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("prepare_pilot_batch", SCRIPT)
prepare_pilot_batch = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = prepare_pilot_batch
spec.loader.exec_module(prepare_pilot_batch)


class PreparePilotBatchTests(unittest.TestCase):
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

    def args(self, record_dir: Path, root: Path, **overrides) -> Namespace:
        values = {
            "record_dir": record_dir.as_posix(),
            "target_root": (root / "pilots").as_posix(),
            "use_suggested_targets": False,
            "out_dir": (root / "packs").as_posix(),
            "max_pilots": 2,
            "notes": "batch test",
            "min_successes": 1,
            "min_score": 90,
            "target_label": "batch-target",
            "limit": 3,
            "allow_low_confidence": False,
            "generated_date": "2026-06-04",
            "created": "2026-06-04T12:00:00Z",
            "generated": "2026-06-04T12:00:00Z",
            "min_records": 5,
            "min_external_or_multi_project": 3,
            "min_domains": 4,
            "min_installed_init_brief": 2,
            "pilot_record_dir": None,
            "pilot_status": "prepared",
            "pilot_notes": "",
            "dry_run": False,
            "force": True,
        }
        values.update(overrides)
        return Namespace(**values)

    def test_dry_run_plans_selected_suggested_pilots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            record_dir.mkdir()
            self.write_payload(record_dir, self.valid_payload())

            payload = prepare_pilot_batch.build_payload(self.args(record_dir, root, dry_run=True))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("dry-run", payload["mode"])
        self.assertEqual(2, payload["selected_count"])
        self.assertEqual("llm-app-pilot", payload["planned_pilots"][0]["slug"])
        self.assertTrue(payload["planned_pilots"][0]["target"].endswith("/pilots/llm-app-pilot"))
        self.assertEqual("planned", payload["prepared"][0]["status"])
        self.assertIn("not usage proof", payload["claim_boundary"])

    def test_prepare_batch_writes_pilot_records(self):
        def fake_prepare(args):
            return {
                "status": "pass",
                "target": args.target,
                "profile": "llm-app",
                "pilot_pack": {
                    "status": "pass",
                    "pack": args.out,
                    "issue_draft": args.issue_out,
                    "harness_label": args.harness_label,
                },
            }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            pilot_records = root / "pilot-records"
            record_dir.mkdir()
            self.write_payload(record_dir, self.valid_payload())
            args = self.args(record_dir, root, max_pilots=1, pilot_record_dir=pilot_records.as_posix())

            with patch.object(prepare_pilot_batch.prepare_pilot, "build_payload", side_effect=fake_prepare):
                payload = prepare_pilot_batch.build_payload(args)

            record_path = Path(payload["pilot_records"][0]["path"])
            record = json.loads(record_path.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("prepare", payload["mode"])
        self.assertEqual(1, payload["selected_count"])
        self.assertEqual("llm-app-pilot", record["slug"])
        self.assertEqual("prepared", record["status"])
        self.assertEqual("generated pilot harness: llm-app-pilot", record["target"])
        self.assertEqual("external", record["source_type"])

    def test_negative_max_pilots_is_rejected(self):
        with self.assertRaises(SystemExit):
            prepare_pilot_batch.selected_pilots({"suggested_pilots": []}, -1)


if __name__ == "__main__":
    unittest.main()

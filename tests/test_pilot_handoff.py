import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_pilot_handoff.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_pilot_handoff", SCRIPT)
export_pilot_handoff = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_pilot_handoff
spec.loader.exec_module(export_pilot_handoff)

import pilot_board


class PilotHandoffTests(unittest.TestCase):
    def pilot_payload(self, root: Path, slug: str = "llm-app-pilot") -> dict:
        pack = root / "LLM_APP_PILOT_PACK.md"
        issue = root / "LLM_APP_USAGE_ISSUE_DRAFT.md"
        pack.write_text("# Pilot Pack\n\nRun one small public-safe task.\n", encoding="utf-8")
        issue.write_text("# Usage Issue Draft\n\n### Evidence\n\n- Public-safe result.\n", encoding="utf-8")
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
                    "pack": pack.as_posix(),
                    "issue_draft": issue.as_posix(),
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
            "out": (root / "handoffs").as_posix(),
            "status": None,
            "slug": None,
            "force": False,
            "no_write": False,
            "json": False,
        }
        values.update(overrides)
        return Namespace(**values)

    def write_record(self, root: Path, slug: str = "llm-app-pilot") -> None:
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        record = pilot_board.build_record(self.pilot_payload(root, slug=slug), status="prepared")
        (record_dir / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def test_build_payload_and_write_handoff_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_record(root)
            args = self.args(root)

            payload = export_pilot_handoff.build_payload(args)
            export_pilot_handoff.write_handoff(Path(args.out), payload, force=False)
            handoff = Path(args.out) / "llm-app-pilot"

            self.assertEqual("pass", payload["status"])
            self.assertEqual("handoff-ready", payload["readiness"])
            self.assertEqual(1, payload["handoff_count"])
            self.assertTrue((handoff / "README.md").exists())
            self.assertTrue((handoff / "REPORTER_MESSAGE.txt").exists())
            self.assertTrue((handoff / "MAINTAINER_COMMANDS.md").exists())
            self.assertEqual("# Pilot Pack", (handoff / "PILOT_PACK.md").read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual("# Usage Issue Draft", (handoff / "USAGE_ISSUE_DRAFT.md").read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("usage-from-issue", (handoff / "MAINTAINER_COMMANDS.md").read_text(encoding="utf-8"))
            self.assertIn("not usage proof", (Path(args.out) / "README.md").read_text(encoding="utf-8"))

    def test_no_active_pilots_previews_without_writing_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pilot-records").mkdir()
            args = self.args(root)

            payload = export_pilot_handoff.build_payload(args)

        self.assertEqual("pass", payload["status"])
        self.assertEqual("no-active-pilots", payload["readiness"])
        self.assertEqual(0, payload["handoff_count"])

    def test_refuses_existing_output_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_record(root)
            args = self.args(root)
            Path(args.out).mkdir()
            (Path(args.out) / "README.md").write_text("existing\n", encoding="utf-8")
            payload = export_pilot_handoff.build_payload(args)

            with self.assertRaises(SystemExit) as raised:
                export_pilot_handoff.write_handoff(Path(args.out), payload, force=False)

        self.assertIn("Output directory is not empty", str(raised.exception))


if __name__ == "__main__":
    unittest.main()

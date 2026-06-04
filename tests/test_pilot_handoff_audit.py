import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

for module_name in ("export_pilot_handoff", "audit_pilot_handoffs"):
    script = REPO_ROOT / "scripts" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

import audit_pilot_handoffs
import export_pilot_handoff
import pilot_board


class PilotHandoffAuditTests(unittest.TestCase):
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

    def write_record(self, root: Path, slug: str = "llm-app-pilot") -> None:
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        record = pilot_board.build_record(self.pilot_payload(root, slug=slug), status="prepared")
        (record_dir / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def args(self, root: Path, **overrides) -> Namespace:
        values = {
            "record_dir": (root / "pilot-records").as_posix(),
            "usage_record_dir": (root / "usage-records").as_posix(),
            "usage_report": (root / "USAGE_RECORDS.md").as_posix(),
            "pilot_board_report": (root / "PILOT_BOARD.md").as_posix(),
            "handoff_dir": (root / "handoffs").as_posix(),
            "report": (root / "PILOT_HANDOFF_AUDIT.md").as_posix(),
            "status": None,
            "slug": None,
            "no_write": False,
            "json": False,
        }
        values.update(overrides)
        return Namespace(**values)

    def write_handoff(self, root: Path) -> Namespace:
        args = self.args(root)
        handoff_args = Namespace(
            record_dir=args.record_dir,
            usage_record_dir=args.usage_record_dir,
            usage_report=args.usage_report,
            pilot_board_report=args.pilot_board_report,
            out=args.handoff_dir,
            status=None,
            slug=None,
            force=False,
            no_write=False,
            json=False,
        )
        payload = export_pilot_handoff.build_payload(handoff_args)
        export_pilot_handoff.write_handoff(Path(args.handoff_dir), payload, force=False)
        return args

    def test_audits_generated_handoff_and_importer_shaped_draft(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_record(root)
            args = self.write_handoff(root)

            payload = audit_pilot_handoffs.build_payload(args)
            audit_pilot_handoffs.write_report(Path(args.report), payload)

            report = Path(args.report).read_text(encoding="utf-8")

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("handoff-audit-ready", payload["readiness"])
        self.assertEqual(1, payload["handoff_count"])
        self.assertEqual("needs-input", payload["records"][0]["usage_report_draft"]["readiness"])
        self.assertEqual(
            "LLM App Workspace Pilot",
            payload["records"][0]["usage_report_draft"]["lint"]["values"]["harness_label"],
        )
        self.assertIn("USAGE_REPORT_DRAFT.md is importer-shaped", payload["warnings"][0])
        self.assertIn("# Pilot Handoff Audit", report)
        self.assertIn("This audit checks whether handoff folders are ready to send", report)

    def test_fails_when_usage_report_draft_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_record(root)
            args = self.write_handoff(root)
            (Path(args.handoff_dir) / "llm-app-pilot" / "USAGE_REPORT_DRAFT.md").unlink()

            payload = audit_pilot_handoffs.build_payload(args)

        self.assertEqual("fail", payload["status"])
        self.assertEqual("handoff-audit-failed", payload["readiness"])
        self.assertIn("Missing required file: USAGE_REPORT_DRAFT.md", payload["errors"][0])

    def test_fails_when_reporter_handoff_omits_next_task_guide(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_record(root)
            args = self.write_handoff(root)
            reporter_handoff = Path(args.handoff_dir) / "llm-app-pilot" / "REPORTER_HANDOFF.md"
            reporter_handoff.write_text(
                reporter_handoff.read_text(encoding="utf-8").replace("NEXT_TASK.md", "Docs/GETTING_STARTED.md"),
                encoding="utf-8",
            )

            payload = audit_pilot_handoffs.build_payload(args)

        self.assertEqual("fail", payload["status"])
        self.assertEqual("handoff-audit-failed", payload["readiness"])
        self.assertIn("REPORTER_HANDOFF.md must point reporters to NEXT_TASK.md.", payload["errors"][0])

    def test_no_active_pilots_is_pass_without_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pilot-records").mkdir()

            payload = audit_pilot_handoffs.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"])
        self.assertEqual("no-active-pilots", payload["readiness"])
        self.assertEqual(0, payload["handoff_count"])


if __name__ == "__main__":
    unittest.main()

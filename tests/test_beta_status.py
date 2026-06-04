import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "beta_status.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("beta_status", SCRIPT)
beta_status = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = beta_status
spec.loader.exec_module(beta_status)


INCOMPLETE_BODY = """### Pilot or usage-record slug

llm-app-pilot

### Domain or project type

LLM app

### Generated harness profile or label

LLM App Workspace Pilot

### Evidence type

private-summary

### Source type

external

### Generation path

installed-quickstart

### Outcome

_no response_

### Public-safe task summary

_no response_

### Evidence

_no response_

### Verification performed

_no response_

### Privacy review

_no response_

### Limitations

_no response_
"""


class BetaStatusTests(unittest.TestCase):
    def args(self, root: Path, **overrides) -> argparse.Namespace:
        values = {
            "record_dir": (root / "usage-records").as_posix(),
            "pilot_record_dir": (root / "pilot-records").as_posix(),
            "usage_report": (root / "USAGE_RECORDS.md").as_posix(),
            "pilot_board_report": (root / "PILOT_BOARD.md").as_posix(),
            "pilot_github_sync_report": (root / "PILOT_GITHUB_SYNC.md").as_posix(),
            "pilot_next_action_report": (root / "PILOT_NEXT_ACTION.md").as_posix(),
            "followup_dir": (root / "pilot-github-followups").as_posix(),
            "repo": "example/repo",
            "gh_bin": "/tmp/fake-gh",
            "generated": "2026-06-04T00:00:00Z",
            "reminder_after_hours": 72,
            "status": None,
            "slug": None,
            "report": (root / "BETA_STATUS.md").as_posix(),
            "min_records": beta_status.usage_gaps.DEFAULT_TARGETS["min_records"],
            "min_external_or_multi_project": beta_status.usage_gaps.DEFAULT_TARGETS["min_external_or_multi_project"],
            "min_domains": beta_status.usage_gaps.DEFAULT_TARGETS["min_domains"],
            "min_installed_init_brief": beta_status.usage_gaps.DEFAULT_TARGETS["min_installed_init_brief"],
            "no_write": False,
            "json": True,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def write_usage_record(self, root: Path) -> None:
        record = {
            "slug": "self-dogfood-docs",
            "title": "Self Dogfood Docs",
            "generated": "2026-06-04T12:00:00Z",
            "domain": "Documentation",
            "harness_path": "examples/live-create/self-dogfood-docs",
            "task_summary": "Used the generated harness on a privacy-safe documentation task.",
            "outcome": "success",
            "evidence_type": "private-summary",
            "source_type": "self-dogfood",
            "generation_path": "repo-dogfood",
            "evidence": ["private summary reviewed", "generated checklist completed"],
            "verification": ["task trial recorded", "privacy review completed"],
            "privacy_review": "Public-safe summary only; no secrets, personal data, private paths, proprietary source, or raw logs.",
            "limitations": ["Single internal task."],
        }
        record_dir = root / "usage-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "self-dogfood-docs.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def write_pilot_record(self, root: Path) -> None:
        record = {
            "claim_boundary": "Preparing a pilot is not usage proof until converted into checked usage evidence.",
            "domain": "LLM app",
            "generated": "2026-06-04T00:00:00Z",
            "generation_path": "installed-quickstart",
            "harness_label": "LLM App Workspace Pilot",
            "issue_draft": "Docs/Environment/issue.md",
            "notes": "opened public pilot issue https://github.com/example/repo/issues/42",
            "pilot_pack": "Docs/Environment/pack.md",
            "profile": "llm-app",
            "selected_index": 1,
            "slug": "llm-app-pilot",
            "source_type": "external",
            "status": "invited",
            "status_history": [{"notes": "opened public pilot issue https://github.com/example/repo/issues/42"}],
            "target": "generated pilot harness: llm-app-pilot",
            "title": "LLM app pilot",
            "usage_record": "",
        }
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "llm-app-pilot.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def github_payload(self) -> dict:
        return {
            "number": 42,
            "title": "External usage pilot: LLM app pilot",
            "url": "https://github.com/example/repo/issues/42",
            "state": "OPEN",
            "body": INCOMPLETE_BODY,
            "comments": [],
        }

    def test_build_payload_summarizes_missing_evidence_and_waiting_pilot_queue(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_usage_record(root)
            self.write_pilot_record(root)

            payload = beta_status.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("missing-beta-exit-evidence", payload["readiness"])
        self.assertFalse(payload["beta_exit_ready"])
        self.assertEqual(4, payload["usage_gaps"]["records"])
        self.assertEqual("waiting-for-reporters", payload["pilot_readiness"])
        self.assertEqual(1, payload["operator_queue"]["waiting_count"])
        self.assertEqual("post-reporter-followup", payload["next_action"]["type"])
        self.assertIn("pilot-github-sync", payload["commands"][1]["command"])
        self.assertIn("not usage proof", payload["claim_boundary"])

    def test_write_report_includes_dashboard_sections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_usage_record(root)
            self.write_pilot_record(root)
            payload = beta_status.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(),
            )
            report = root / "BETA_STATUS.md"

            beta_status.write_report(report, payload)
            text = report.read_text(encoding="utf-8")

        self.assertIn("# Beta Status", text)
        self.assertIn("## Evidence Gap", text)
        self.assertIn("## Pilot Queue", text)
        self.assertIn("## Next Action", text)
        self.assertIn("codex-harness doctor --beta-exit", text)


if __name__ == "__main__":
    unittest.main()

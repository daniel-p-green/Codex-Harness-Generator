import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "usage_from_github_issue.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("usage_from_github_issue", SCRIPT)
usage_from_github_issue = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = usage_from_github_issue
spec.loader.exec_module(usage_from_github_issue)

import pilot_board


ISSUE_BODY = """### Pilot or usage-record slug

external-llm-app

### Domain or project type

LLM app

### Generated harness profile or label

llm-app profile

### Evidence type

private-summary

### Source type

external

### Generation path

installed-init-brief

### Outcome

success

### Public-safe task summary

The generated harness helped organize prompts, evals, and source-grounded review steps.

### Evidence

- Generated AGENTS.md matched the project shape.
- The harness made verification steps explicit.

### Verification performed

- Ran the generated smoke check successfully.
- Completed one real task using the generated reviewer guidance.

### Privacy review

Removed private repo names, local paths, customer details, credentials, and raw logs.

### Limitations

- One project and one task.
"""


class UsageFromGithubIssueTests(unittest.TestCase):
    def args(self, root: Path, **overrides) -> argparse.Namespace:
        values = {
            "issue": "12",
            "repo": "daniel-p-green/Codex-Harness-Generator",
            "gh_bin": "gh",
            "slug": None,
            "title": None,
            "harness_label": None,
            "source_type": None,
            "generation_path": None,
            "generated": "2026-06-04T00:00:00Z",
            "record_dir": (root / "usage-records").as_posix(),
            "report": (root / "USAGE_RECORDS.md").as_posix(),
            "pilot_record_dir": (root / "pilot-records").as_posix(),
            "pilot_board_report": (root / "PILOT_BOARD.md").as_posix(),
            "pilot_notes": "converted from GitHub issue",
            "force": False,
            "lint_only": False,
            "no_write": True,
            "json": True,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def github_payload(self, body: str = ISSUE_BODY) -> dict:
        return {
            "number": 12,
            "title": "External usage pilot: LLM app pilot",
            "url": "https://github.com/example/repo/issues/12",
            "state": "OPEN",
            "body": body,
        }

    def write_matching_pilot_record(self, root: Path) -> None:
        payload = {
            "generated": "2026-06-04T00:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": "external-llm-app",
                "title": "External LLM app report",
                "domain": "LLM app",
                "profile": "llm-app",
                "source_type": "external",
                "generation_path": "installed-init-brief",
                "project_name": "External LLM App Pilot",
            },
            "prepared_pilot": {
                "target": "/tmp/external-llm-app",
                "pilot_pack": {
                    "harness_label": "llm-app profile",
                    "pack": "/tmp/PILOT_PACK.md",
                    "issue_draft": "/tmp/ISSUE.md",
                },
            },
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
        }
        pilot_record_dir = root / "pilot-records"
        pilot_record_dir.mkdir(parents=True, exist_ok=True)
        pilot_board.write_record(
            pilot_record_dir / "external-llm-app.json",
            pilot_board.build_record(payload),
            force=True,
        )

    def test_lint_only_uses_existing_issue_importer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_matching_pilot_record(root)

            payload = usage_from_github_issue.build_payload(
                self.args(root, lint_only=True),
                github_payload=self.github_payload(),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("conversion-ready", payload["readiness"])
        self.assertEqual(12, payload["github_issue"]["number"])
        self.assertEqual("external-llm-app", payload["slug"])

    def test_no_write_previews_record_with_github_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_matching_pilot_record(root)

            payload = usage_from_github_issue.build_payload(
                self.args(root, no_write=True),
                github_payload=self.github_payload(),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertFalse(payload["written"])
        self.assertEqual("external-llm-app", payload["record"]["slug"])
        self.assertEqual("https://github.com/example/repo/issues/12", payload["github_issue"]["url"])

    def test_write_converts_matching_pilot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_matching_pilot_record(root)

            payload = usage_from_github_issue.build_payload(
                self.args(root, no_write=False),
                github_payload=self.github_payload(),
            )

            usage_record = root / "usage-records" / "external-llm-app.json"
            usage_record_exists = usage_record.exists()
            pilot_record = json.loads((root / "pilot-records" / "external-llm-app.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["written"])
        self.assertTrue(usage_record_exists)
        self.assertEqual("converted", pilot_record["status"])
        self.assertEqual("external-llm-app", pilot_record["usage_record"])

    def test_missing_gh_binary_has_clean_error(self):
        with self.assertRaises(SystemExit) as context:
            usage_from_github_issue.fetch_github_issue("12", gh_bin="/definitely/missing/gh")

        self.assertIn("gh executable not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()

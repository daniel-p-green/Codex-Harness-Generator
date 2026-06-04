import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATE = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "external-usage-report.yml"
EVIDENCE_DOC = REPO_ROOT / "Docs" / "Environment" / "EXTERNAL_USAGE_EVIDENCE.md"
ISSUE_EXAMPLE = REPO_ROOT / "Docs" / "Environment" / "EXTERNAL_USAGE_ISSUE_EXAMPLE.md"


class ExternalUsageEvidenceTests(unittest.TestCase):
    def test_issue_template_collects_required_public_safe_fields(self):
        text = ISSUE_TEMPLATE.read_text(encoding="utf-8")

        self.assertIn("name: External usage report", text)
        for field_id in (
            "pilot_slug",
            "domain",
            "harness_label",
            "evidence_type",
            "source_type",
            "generation_path",
            "outcome",
            "task_summary",
            "evidence",
            "verification",
            "privacy_review",
            "limitations",
        ):
            self.assertIn(f"id: {field_id}", text)
        for evidence_type in ("sanitized", "private-summary", "synthetic"):
            self.assertIn(f"- {evidence_type}", text)
        for source_type in ("external", "multi-project", "self-dogfood"):
            self.assertIn(f"- {source_type}", text)
        for generation_path in ("installed-init-brief", "installed-quickstart", "installed-init-from-project", "adoption-plan", "manual-migration"):
            self.assertIn(f"- {generation_path}", text)
        for outcome in ("success", "partial", "inconclusive", "failed"):
            self.assertIn(f"- {outcome}", text)

    def test_issue_template_warns_against_sensitive_public_content(self):
        text = ISSUE_TEMPLATE.read_text(encoding="utf-8")

        for phrase in (
            "Do not include secrets",
            "customer data",
            "candidate data",
            "proprietary source",
            "private repository paths",
            "local machine paths",
            "email addresses",
            "access tokens",
            "raw private transcripts",
        ):
            self.assertIn(phrase, text)

    def test_external_evidence_doc_explains_maintainer_conversion(self):
        text = EVIDENCE_DOC.read_text(encoding="utf-8")

        self.assertIn("# External Usage Evidence", text)
        self.assertIn("python scripts/codex_harness.py pilot-pack", text)
        self.assertIn("python scripts/codex_harness.py usage-from-harness", text)
        self.assertIn("python scripts/codex_harness.py usage-from-issue", text)
        self.assertIn("Docs/Environment/EXTERNAL_USAGE_ISSUE_EXAMPLE.md", text)
        self.assertIn("Pilot or usage-record slug", text)
        self.assertIn("python scripts/codex_harness.py usage-record", text)
        self.assertIn("--evidence-type private-summary", text)
        self.assertIn("--source-type external", text)
        self.assertIn("--generation-path installed-quickstart", text)
        self.assertIn("--pilot-record-dir Docs/Environment/pilot-records", text)
        self.assertIn("--no-write", text)
        self.assertIn("python scripts/codex_harness.py usage-validate", text)
        self.assertIn("Do not claim broad adoption", text)

    def test_checked_issue_example_lints_and_previews_without_writing(self):
        lint = subprocess.run(
            [
                sys.executable,
                "scripts/codex_harness.py",
                "usage-from-issue",
                ISSUE_EXAMPLE.as_posix(),
                "--title",
                "Example external usage issue",
                "--lint-only",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, lint.returncode, lint.stdout + lint.stderr)
        lint_payload = json.loads(lint.stdout)
        self.assertEqual("pass", lint_payload["status"])
        self.assertEqual("conversion-ready", lint_payload["readiness"])
        self.assertIn("Synthetic usage", " ".join(lint_payload["warnings"]))

        preview = subprocess.run(
            [
                sys.executable,
                "scripts/codex_harness.py",
                "usage-from-issue",
                ISSUE_EXAMPLE.as_posix(),
                "--title",
                "Example external usage issue",
                "--no-write",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, preview.returncode, preview.stdout + preview.stderr)
        preview_payload = json.loads(preview.stdout)
        self.assertFalse(preview_payload["written"])
        self.assertEqual("example-external-issue", preview_payload["record"]["slug"])
        self.assertEqual("synthetic", preview_payload["record"]["evidence_type"])


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATE_ROOT = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
WORKFLOW_ROOT = REPO_ROOT / ".github" / "workflows"
ROADMAP = REPO_ROOT / "Docs" / "Environment" / "ROADMAP.md"


class ProjectSupportFilesTests(unittest.TestCase):
    def test_public_issue_templates_exist(self):
        for filename in (
            "bug-report.yml",
            "feature-request.yml",
            "external-usage-report.yml",
        ):
            self.assertTrue((ISSUE_TEMPLATE_ROOT / filename).is_file(), filename)

    def test_usage_evidence_lint_workflow_exists(self):
        text = (WORKFLOW_ROOT / "usage-evidence-lint.yml").read_text(encoding="utf-8")

        for phrase in (
            "Usage Evidence Lint",
            "usage-from-github-issue",
            "--include-comments",
            "--lint-only",
            "format_usage_lint_comment.py",
            "codex-harness-usage-lint",
            "issues: write",
        ):
            self.assertIn(phrase, text)

    def test_bug_report_template_requests_reproduction_and_privacy_review(self):
        text = (ISSUE_TEMPLATE_ROOT / "bug-report.yml").read_text(encoding="utf-8")

        for phrase in (
            "Reproduction steps",
            "Expected behavior",
            "Actual behavior",
            "Checks run",
            "Privacy review",
            "Do not include secrets",
            "local machine paths",
            "raw private logs",
        ):
            self.assertIn(phrase, text)

    def test_feature_request_template_requests_problem_and_verification_evidence(self):
        text = (ISSUE_TEMPLATE_ROOT / "feature-request.yml").read_text(encoding="utf-8")

        for phrase in (
            "Problem",
            "Proposed improvement",
            "Evidence or example",
            "How we would verify it",
            "Privacy review",
        ):
            self.assertIn(phrase, text)

    def test_roadmap_defines_beta_exit_criteria(self):
        text = ROADMAP.read_text(encoding="utf-8")

        for phrase in (
            "# Roadmap",
            "Beta Exit Criteria",
            "At least 5 non-synthetic usage records",
            "At least 3 records are from external or multi-project usage",
            "At least 4 different domains",
            "installed brief-based generation",
            "source-freshness",
            "semantic-alignment",
            "short demo capture",
            "do not claim a milestone is done until the linked",
            "proof exists in this repository",
        ):
            self.assertIn(phrase, text)

    def test_roadmap_documents_public_pilot_github_followup_loop(self):
        text = ROADMAP.read_text(encoding="utf-8")

        for phrase in (
            "codex-harness pilot-github-issues",
            "codex-harness pilot-reporter-replies",
            "codex-harness pilot-github-sync",
            "Docs/Environment/PILOT_GITHUB_SYNC.md",
            "Docs/Environment/pilot-github-followups",
            "gh issue comment --body-file",
            "pilot_github_followups",
            "codex-harness usage-from-github-issue --include-comments",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_upstream_drift.py"
UPSTREAM_REF = "source-upstream/main"
LEGACY_INSTRUCTION_FILE = "CL" + "AUDE.md"

spec = importlib.util.spec_from_file_location("check_upstream_drift", SCRIPT)
check_upstream_drift = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(check_upstream_drift)


class UpstreamDriftTests(unittest.TestCase):
    def args(self, **overrides):
        values = {
            "upstream": UPSTREAM_REF,
            "target": "HEAD",
            "sample_limit": 5,
            "commit_limit": 3,
            "generated": "2026-06-04T12:00:00Z",
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def fake_git(self, command, *, check=True):
        key = tuple(command)
        responses = {
            ("merge-base", UPSTREAM_REF, "HEAD"): "base-full",
            ("rev-parse", "--short", UPSTREAM_REF): "abc1234",
            ("rev-parse", "--short", "HEAD"): "def5678",
            ("rev-parse", "--short", "base-full"): "999aaaa",
            ("rev-list", "--left-right", "--count", f"{UPSTREAM_REF}...HEAD"): "2\t7",
            ("diff", "--name-status", f"{UPSTREAM_REF}...HEAD"): (
                "M\tREADME.md\n"
                "A\tDocs/Environment/PROOF_STATUS.md\n"
                f"R084\t{LEGACY_INSTRUCTION_FILE}\tAGENTS.md\n"
            ),
            ("log", "--oneline", "-3", f"HEAD..{UPSTREAM_REF}"): "abc1234 upstream change",
            ("log", "--oneline", "-3", f"{UPSTREAM_REF}..HEAD"): "def5678 codex change",
        }
        return responses.get(key, "")

    def test_build_payload_reports_ahead_behind_and_changed_areas(self):
        with patch.object(check_upstream_drift, "run_git", side_effect=self.fake_git):
            payload = check_upstream_drift.build_payload(self.args())

        self.assertEqual("pass", payload["status"])
        self.assertEqual("upstream-review-needed", payload["readiness"])
        self.assertEqual({"upstream_only": 2, "target_only": 7}, payload["ahead_behind"])
        self.assertEqual(3, payload["changed_file_count"])
        areas = {item["area"] for item in payload["changed_areas"]}
        self.assertIn("Docs", areas)
        self.assertIn("README.md", areas)
        self.assertEqual(LEGACY_INSTRUCTION_FILE, payload["sample_changed_files"][2]["previous_path"])
        self.assertEqual(["abc1234 upstream change"], payload["recent_upstream_commits"])

    def test_build_payload_marks_current_when_no_upstream_only_commits(self):
        def fake_git(command, *, check=True):
            if tuple(command) == ("rev-list", "--left-right", "--count", f"{UPSTREAM_REF}...HEAD"):
                return "0\t4"
            return self.fake_git(command, check=check)

        with patch.object(check_upstream_drift, "run_git", side_effect=fake_git):
            payload = check_upstream_drift.build_payload(self.args())

        self.assertEqual("codex-fork-current-with-upstream", payload["readiness"])
        self.assertEqual([], payload["review_needed"])

    def test_write_report_includes_claim_boundary(self):
        payload = {
            "generated": "2026-06-04T12:00:00Z",
            "status": "pass",
            "readiness": "upstream-review-needed",
            "upstream": UPSTREAM_REF,
            "target": "HEAD",
            "upstream_rev": "abc1234",
            "target_rev": "def5678",
            "merge_base": "999aaaa",
            "ahead_behind": {"upstream_only": 1, "target_only": 2},
            "changed_file_count": 1,
            "changed_areas": [{"area": "Docs", "count": 1}],
            "sample_changed_files": [{"status": "M", "path": "Docs/example.md", "previous_path": ""}],
            "recent_upstream_commits": ["abc1234 upstream change"],
            "recent_target_commits": ["def5678 codex change"],
            "claim_boundary": "This audit does not prove semantic equivalence.",
            "review_needed": ["Review upstream-only commits."],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "UPSTREAM_DRIFT.md"
            check_upstream_drift.write_report(report, payload)
            text = report.read_text(encoding="utf-8")

        self.assertIn("# Upstream Drift", text)
        self.assertIn("Readiness: upstream-review-needed", text)
        self.assertIn("does not prove semantic equivalence", text)
        self.assertIn("abc1234 upstream change", text)


if __name__ == "__main__":
    unittest.main()

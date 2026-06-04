import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPO_ROOT / "scripts" / "profile_catalog.py"
sys.path.insert(0, (REPO_ROOT / "scripts").as_posix())

spec = importlib.util.spec_from_file_location("profile_catalog", CATALOG_PATH)
profile_catalog = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = profile_catalog
spec.loader.exec_module(profile_catalog)


class ProfileCatalogTests(unittest.TestCase):
    def test_catalog_payload_includes_all_profiles(self):
        payload = profile_catalog.catalog_payload()

        self.assertEqual("pass", payload["status"])
        self.assertEqual(20, payload["profile_count"])
        self.assertEqual(20, payload["total_supported_profiles"])
        slugs = [profile["slug"] for profile in payload["profiles"]]
        self.assertIn("software-development", slugs)
        self.assertIn("security-audit", slugs)

    def test_single_profile_payload_includes_guardrails(self):
        payload = profile_catalog.catalog_payload("security-audit")

        self.assertEqual(1, payload["profile_count"])
        profile = payload["profiles"][0]
        self.assertEqual("security-audit", profile["slug"])
        self.assertEqual("domain", profile["kind"])
        self.assertTrue(profile["extra_guidance"])

    def test_recommendation_payload_ranks_matching_profile_first(self):
        payload = profile_catalog.recommendation_payload(
            "We need a RAG app with prompts, evals, retrieval quality checks, and tool calls.",
            limit=3,
        )

        self.assertEqual("pass", payload["status"])
        self.assertGreaterEqual(payload["recommendation_count"], 1)
        self.assertEqual("high", payload["confidence"])
        self.assertEqual("llm-app", payload["recommendations"][0]["slug"])
        self.assertEqual("high", payload["recommendations"][0]["confidence"])
        self.assertGreater(payload["recommendations"][0]["score"], 0)
        self.assertIn("rag", payload["recommendations"][0]["matched_terms"])

    def test_recommendation_payload_marks_no_match(self):
        payload = profile_catalog.recommendation_payload("zzqx plorn mivv", limit=2)

        self.assertEqual("none", payload["confidence"])
        self.assertIn("full /create custom intake", payload["guidance"])
        self.assertEqual("none", payload["recommendations"][0]["confidence"])

    def test_recommendation_payload_handles_high_risk_domains(self):
        payload = profile_catalog.recommendation_payload(
            "Security audit for CVE exposure, vulnerability triage, threat model, and safe remediation.",
            limit=1,
        )

        self.assertEqual("security-audit", payload["recommendations"][0]["slug"])

    def test_cli_json_output_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "scripts/profile_catalog.py", "--profile", "legal-research", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("legal-research", payload["profiles"][0]["slug"])

    def test_cli_text_output_is_user_facing(self):
        completed = subprocess.run(
            [sys.executable, "scripts/profile_catalog.py", "--profile", "customer-support"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("customer-support (domain)", completed.stdout)
        self.assertIn("First tasks:", completed.stdout)
        self.assertIn("Guardrails:", completed.stdout)

    def test_cli_recommendation_text_output_is_user_facing(self):
        completed = subprocess.run(
            [
                sys.executable,
                "scripts/profile_catalog.py",
                "--recommend",
                "Hiring pipeline with candidate scorecards, interview rubric, and fairness review.",
                "--limit",
                "2",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("Recommended deterministic profiles", completed.stdout)
        self.assertIn("confidence=high", completed.stdout)
        self.assertIn("hiring-pipeline", completed.stdout)


if __name__ == "__main__":
    unittest.main()

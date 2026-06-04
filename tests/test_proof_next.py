import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "proof_next.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("proof_next", SCRIPT)
proof_next = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = proof_next
spec.loader.exec_module(proof_next)


class ProofNextTests(unittest.TestCase):
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

    def args(self, record_dir: Path, report: Path | None = None, pilot_record_dir: Path | None = None) -> argparse.Namespace:
        return argparse.Namespace(
            target="/tmp/next-pilot",
            record_dir=record_dir.as_posix(),
            pilot_record_dir=(pilot_record_dir or record_dir / "pilot-records").as_posix(),
            pilot_board_report="Docs/Environment/PILOT_BOARD.md",
            usage_report="Docs/Environment/USAGE_RECORDS.md",
            pilot_pack_out="/tmp/NEXT_EXTERNAL_PILOT_PACK.md",
            issue_out="/tmp/NEXT_EXTERNAL_USAGE_ISSUE_DRAFT.md",
            report=(report or record_dir / "PROOF_NEXT.md").as_posix(),
            min_records=5,
            min_external_or_multi_project=3,
            min_domains=4,
            min_installed_init_brief=2,
            no_write=False,
            json=False,
        )

    def write_payload(self, root: Path, payload: dict) -> None:
        (root / f"{payload['slug']}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def write_pilot_record(self, root: Path, status: str = "prepared") -> None:
        root.mkdir(parents=True, exist_ok=True)
        record = {
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
            "domain": "LLM app",
            "generated": "2026-06-04T12:00:00Z",
            "generation_path": "installed-quickstart",
            "harness_label": "LLM App Workspace Pilot",
            "issue_draft": "Docs/Environment/LLM_APP_USAGE_ISSUE_DRAFT.md",
            "notes": "",
            "pilot_pack": "Docs/Environment/LLM_APP_PILOT_PACK.md",
            "profile": "llm-app",
            "selected_index": 1,
            "slug": "llm-app-pilot",
            "source_type": "external",
            "status": status,
            "target": "/private/tmp/codex-llm-app-pilot",
            "title": "LLM app pilot",
            "usage_record": "",
        }
        (root / "llm-app-pilot.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_build_payload_turns_usage_gaps_into_operator_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, self.valid_payload())

            payload = proof_next.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("missing-beta-exit-evidence", payload["readiness"])
        self.assertEqual("llm-app", payload["next_pilot"]["profile"])
        commands = [item["command"] for item in payload["command_sequence"]]
        self.assertTrue(any("codex-harness prepare-next-pilot /tmp/next-pilot" in command for command in commands))
        self.assertTrue(any("codex-harness pilot-board" in command for command in commands))
        self.assertTrue(any("codex-harness usage-from-issue" in command for command in commands))
        self.assertTrue(any("codex-harness usage-from-harness <generated-harness>" in command for command in commands))
        self.assertTrue(any("usage-from-issue <completed-issue.md>" in command and "--no-write --json" in command for command in commands))
        self.assertTrue(any("usage-from-harness <generated-harness>" in command and "--no-write --json" in command for command in commands))
        self.assertTrue(any("codex-harness proof-status --beta-exit" in command for command in commands))
        self.assertIn("does not itself prove", payload["claim_boundary"])
        self.assertIsNone(payload["active_pilot"])

    def test_build_payload_continues_active_pilot_instead_of_repreparing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            pilot_record_dir = root / "pilot-records"
            record_dir.mkdir()
            self.write_payload(record_dir, self.valid_payload())
            self.write_pilot_record(pilot_record_dir)

            payload = proof_next.build_payload(self.args(record_dir, pilot_record_dir=pilot_record_dir))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("llm-app-pilot", payload["active_pilot"]["slug"])
        commands = [item["command"] for item in payload["command_sequence"]]
        self.assertFalse(any("prepare-next-pilot" in command for command in commands))
        self.assertTrue(any("pilot-update llm-app-pilot --status invited" in command for command in commands))
        self.assertTrue(any("usage-from-issue <completed-issue.md> --slug llm-app-pilot" in command for command in commands))
        self.assertTrue(any("usage-from-harness <generated-harness> --slug llm-app-pilot" in command for command in commands))
        self.assertTrue(any("usage-from-issue <completed-issue.md>" in command and "--no-write --json" in command for command in commands))
        self.assertTrue(any("usage-from-harness <generated-harness>" in command and "--no-write --json" in command for command in commands))

    def test_write_report_includes_next_pilot_and_claim_boundary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, self.valid_payload())
            report = root / "PROOF_NEXT.md"
            payload = proof_next.build_payload(self.args(root, report))

            proof_next.write_report(report, payload)

            text = report.read_text(encoding="utf-8")

        self.assertIn("# Proof Next Actions", text)
        self.assertIn("## Next Pilot", text)
        self.assertIn("codex-harness prepare-next-pilot", text)
        self.assertIn("codex-harness usage-from-harness", text)
        self.assertIn("codex-harness usage-from-issue", text)
        self.assertIn("--no-write --json", text)
        self.assertIn("This does not prove", text)

    def test_write_report_names_active_pilot_when_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            record_dir = root / "records"
            pilot_record_dir = root / "pilot-records"
            record_dir.mkdir()
            self.write_payload(record_dir, self.valid_payload())
            self.write_pilot_record(pilot_record_dir)
            report = root / "PROOF_NEXT.md"
            payload = proof_next.build_payload(self.args(record_dir, report, pilot_record_dir=pilot_record_dir))

            proof_next.write_report(report, payload)

            text = report.read_text(encoding="utf-8")

        self.assertIn("## Active Pilot", text)
        self.assertIn("Continue this pilot instead of preparing a duplicate.", text)

    def test_ready_payload_has_no_next_pilot(self):
        records = []
        for index, (slug, domain, source_type, generation_path) in enumerate(
            [
                ("external-llm-app", "LLM app", "external", "installed-init-brief"),
                ("multi-project-docs", "Documentation", "multi-project", "installed-quickstart"),
                ("external-data-tool", "Data tooling", "external", "installed-init-from-project"),
                ("self-dogfood-cli", "CLI tooling", "self-dogfood", "manual-migration"),
                ("self-dogfood-evals", "Evaluation", "self-dogfood", "repo-dogfood"),
            ]
        ):
            payload = self.valid_payload(slug)
            payload["domain"] = domain
            payload["source_type"] = source_type
            payload["generation_path"] = generation_path
            payload["generated"] = f"2026-06-04T12:0{index}:00Z"
            records.append(payload)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for payload in records:
                self.write_payload(root, payload)

            result = proof_next.build_payload(self.args(root))

        self.assertEqual("beta-exit-evidence-ready", result["readiness"])
        self.assertIsNone(result["next_pilot"])
        self.assertFalse(any("prepare-next-pilot" in item["command"] for item in result["command_sequence"]))


if __name__ == "__main__":
    unittest.main()

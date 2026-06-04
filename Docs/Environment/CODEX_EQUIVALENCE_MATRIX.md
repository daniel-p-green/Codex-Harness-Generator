# Codex Equivalence Matrix

Generated: 2026-06-04T11:25:44Z
Status: PASS

This matrix maps the earlier harness-generator responsibilities to the
Codex-native surface in this repository. It proves checked-in parity of
structure and workflow coverage, not external adoption or production
performance.

| Capability | Status | Original responsibility | Codex-native surface | Evidence | Commands |
|---|---|---|---|---|---|
| Project instruction contract | PASS | Durable project-level operating instructions. | AGENTS.md plus generated AGENTS.md files. | `AGENTS.md`<br>`scripts/generate_minimal_harness.py`<br>`tests/test_generated_harness_contract.py` | `codex-harness validate <generated-harness>` |
| Codex configuration | PASS | Portable runtime configuration and permission posture. | .codex/config.toml, permission profiles, and config templates. | `.codex/config.toml`<br>`Docs/Templates/Core/codex-config-toml.md`<br>`scripts/eval_codex_port.py` | `python scripts/eval_codex_port.py` |
| Subagents | PASS | Specialized workers for intake, architecture, generation, validation, and upgrade work. | .codex/agents/*.toml plus generated reviewer agents. | `.codex/agents`<br>`Docs/Templates/Agents`<br>`tests/test_eval_codex_port.py` | `codex-harness validate <generated-harness>` |
| Skills | PASS | Reusable triggered workflows for create, validate, update, and upgrade paths. | .agents/skills/*/SKILL.md plus generated health-check skills. | `.agents/skills`<br>`scripts/eval_codex_port.py`<br>`tests/test_eval_codex_port.py` | `python scripts/eval_codex_port.py` |
| Profile catalog | PASS | Domain-specific starting points instead of one generic setup. | 20 deterministic starter profiles with brief-based recommendation. | `scripts/profile_catalog.py`<br>`Docs/StarterProfiles`<br>`tests/test_profile_catalog.py` | `codex-harness profiles`<br>`codex-harness recommend <brief>` |
| Generation | PASS | Create a ready-to-use harness directory. | codex-harness init/generate/brief-acceptance/create-acceptance flows. | `scripts/generate_minimal_harness.py`<br>`scripts/run_brief_acceptance.py`<br>`examples/brief-acceptance` | `codex-harness init <target> --brief <brief>`<br>`codex-harness brief-acceptance <target> --brief <brief>` |
| Validation | PASS | Verify generated environments before trusting them. | Generated local checks, repo evals, smoke tests, and validation reports. | `scripts/validate_generated_harness.py`<br>`scripts/eval_generated_harness.py`<br>`scripts/smoke_generated_harness.py` | `codex-harness validate <generated-harness>`<br>`codex-harness gate` |
| Existing-project adoption | PASS | Adopt a harness into an existing project without overwriting work. | Project inspection, adoption plans, add-only copy scripts, and migration audit. | `scripts/inspect_project.py`<br>`scripts/plan_project_adoption.py`<br>`scripts/migration_audit.py` | `codex-harness inspect <path>`<br>`codex-harness adoption-plan <path>`<br>`codex-harness migration-audit <path>` |
| Copied-harness autonomy | PASS | A copied harness should keep working away from the generator repo. | Generated local check, local eval report, task-trial recorder, and improvement recorder. | `tests/test_generated_harness_contract.py`<br>`examples/deterministic/software-development/scripts/run-harness-evals.py` | `codex-harness local-eval <generated-harness>` |
| High-risk guardrails | PASS | Domain guardrails for risky work. | Profile-specific guardrails and evaluator failures for missing boundaries. | `scripts/generate_minimal_harness.py`<br>`tests/test_generated_harness_contract.py`<br>`Docs/DomainLibrary` | `python -m unittest tests.test_generated_harness_contract -q` |
| Usage evidence | PASS | Record whether generated harnesses actually help with real tasks. | Usage records, validation thresholds, gap reporting, pilot packs, and pilot campaigns. | `Docs/Environment/USAGE_RECORDS.md`<br>`Docs/Environment/USAGE_GAPS.md`<br>`Docs/Environment/PILOT_CAMPAIGN.md`<br>`scripts/record_usage_case.py` | `codex-harness usage-validate`<br>`codex-harness usage-gaps`<br>`codex-harness pilot-campaign` |
| Release proof | PASS | A single readiness view before public claims. | Proof status, proof matrix, eval trends, source freshness, and semantic alignment. | `Docs/Environment/PROOF_STATUS.md`<br>`Docs/Environment/PROOF_MATRIX.md`<br>`scripts/proof_status.py` | `codex-harness proof-status`<br>`codex-harness gate` |

# Proof Matrix

Generated: 2026-06-04

This matrix ties public claims to files and commands that can be inspected in
this repository. It is intentionally conservative: passing evidence below proves
the stated scope, not more.

## Claims And Evidence

| Claim | Evidence artifact | Verification command | Proven scope |
|---|---|---|---|
| The repo is structurally Codex-native. | `AGENTS.md`, `.codex/config.toml`, `.codex/agents/*.toml`, `.agents/skills/*/SKILL.md`, `Docs/Environment/CODEX_PORT_EVALUATION.md` | `python scripts/eval_codex_port.py` | Root generator files use Codex paths, TOML schemas, permission profiles, and official-source citations without legacy platform residue. |
| Generated harness fixtures satisfy the local contract. | `tests/fixtures/generated_harnesses/` | `python scripts/eval_generated_harness.py tests/fixtures/generated_harnesses/*` | Representative generated harnesses pass required-path, config, agent, skill, source-map, manifest, assumptions, and safety checks. |
| Generated harnesses can be read and resolved offline. | `tests/fixtures/generated_harnesses/`, `examples/deterministic/`, `examples/create-acceptance/` | `python scripts/smoke_generated_harness.py <harness-paths>` | Codex-facing files parse, referenced agents and skills resolve, and smoke checks do not require live auth. |
| The deterministic profile generator covers the four base starter profiles. | `scripts/generate_minimal_harness.py`, `scripts/eval_deterministic_profiles.py`, `examples/deterministic/` | `python scripts/eval_deterministic_profiles.py` | `software-development`, `knowledge-work`, `data-analysis`, and `devops-infrastructure` each produce a valid minimal harness. |
| Checked-in deterministic examples are reproducible. | `scripts/refresh_deterministic_examples.py`, `examples/deterministic/` | `python scripts/refresh_deterministic_examples.py && python scripts/run_evals.py` | Example snapshots can be regenerated and are evaluated and smoke-checked by the release gate. |
| The `/create` trigger handoff is contract-tested. | `scripts/simulate_create_trigger.py`, `tests/test_create_trigger_contract.py` | `pytest -q tests/test_create_trigger_contract.py` | Fresh targets, existing environments, hub add-area detection, and interrupted-generation resume write the expected `CREATION_CONTEXT.md` shape. |
| The deterministic preset `/create` acceptance flow works as one target-level artifact. | `scripts/run_create_acceptance.py`, `examples/create-acceptance/*/Docs/Environment/CREATE_ACCEPTANCE_REPORT.md` | `python scripts/run_create_acceptance.py /tmp/codex-create-acceptance --profile software-development --force` | Trigger context, preset harness generation, eval, smoke, manifest, and acceptance report work together in one directory. |
| Checked-in create-acceptance examples cover every base starter profile. | `examples/create-acceptance/` | `python scripts/eval_generated_harness.py examples/create-acceptance/* && python scripts/smoke_generated_harness.py examples/create-acceptance/*` | Each base profile has an inspectable trigger-plus-generated-harness snapshot with `CREATION_CONTEXT.md` and `CREATE_ACCEPTANCE_REPORT.md`. |
| The standard release gate is CI-safe and offline. | `scripts/run_evals.py`, `.github/workflows/evals.yml` | `python scripts/run_evals.py` | Static port checks, fixture evals, offline smokes, deterministic generation, checked-in examples, unit/mutation tests, and compile checks pass without authenticated live services. |
| Authenticated local live smoke works through Codex CLI. | `scripts/smoke_generated_harness.py`, `scripts/run_evals.py --codex-live` | `python scripts/run_evals.py --codex-live` | On a machine with authenticated Codex CLI, checked-in create-acceptance examples can be loaded through non-interactive `codex exec`. |

## Full Local Gate

Run before release or public claims:

```bash
python scripts/run_evals.py
```

Run on an authenticated maintainer machine when live Codex CLI coverage is
available:

```bash
python scripts/run_evals.py --codex-live
```

To live-smoke every checked-in create-acceptance profile:

```bash
python scripts/run_evals.py --codex-live --codex-live-profile all
```

## What This Does Not Prove

- It does not prove that every live model-mediated `/create` interview will
  produce an ideal custom harness on the first attempt.
- It does not prove domain-specific quality for every bundled domain preset.
- It does not prove organization-level compliance, policy enforcement, or
  production security controls.
- It does not prove future Codex docs or config schema compatibility after docs
  drift; that is why static source checks and scheduled evals remain required.

## Remaining Product-Proof Work

- Run several fresh live `/create` sessions in temporary projects and add the
  best sanitized outputs under `examples/live-create/`.
- Add per-domain generated examples for high-stakes domains such as security,
  legal, finance, hiring, and support.
- Add score trend capture so eval regressions are visible over time.
- Add source freshness checks for official OpenAI documentation citations.

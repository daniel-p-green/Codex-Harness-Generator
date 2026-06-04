# Architecture Review

Generated: 2026-06-04

## Summary

Codex Harness Generator is worth continuing if it stays honest about what it is:
a Codex-native, artifact-first harness authoring workflow with deterministic
evals around the generated outputs. It is not a conventional scaffold CLI, and
it should not claim that a model-mediated generation run is automatically
correct without validation.

## Architecture Dissection

The core layer choices are directionally right for Codex:

- `AGENTS.md` carries always-loaded project behavior.
- `.codex/config.toml` carries model, sandbox, permission, agent, skill, MCP, and
  hook configuration.
- `.codex/agents/*.toml` keeps specialist instructions out of the main context.
- `.agents/skills/*/SKILL.md` uses progressive disclosure for triggerable work.
- `Docs/Environment/` records intake, architecture, assumptions, source mapping,
  manifest, and validation output.
- `scripts/run_evals.py` gives the repo a single local release gate.

The strongest decision is artifact-first handoff. Architecture, assumptions, and
validation records are reviewable on disk instead of being trapped in a chat
transcript.

## Stress-Tested Assumptions

- Assumption: Codex can reliably follow a multi-pass generation pipeline.
  Limit: the pipeline is still model-mediated. Verify with generated fixtures,
  smoke checks, and live artifact review.
- Assumption: templates stay aligned with current Codex docs.
  Limit: docs and config schemas can change. Verify with the static port eval and
  periodic source-map refreshes.
- Assumption: one intake can produce a useful harness.
  Limit: real teams discover workflow friction after use. Verify with
  self-learning logs and `/upgrade-environment`.
- Assumption: golden fixtures represent real generated outputs.
  Limit: fixtures are proxies. Verify with fresh sample generations before major
  releases.
- Assumption: public users understand the repo runs inside Codex.
  Limit: without clear docs, users may expect a normal generator binary. Verify
  README and onboarding copy against actual first-run behavior.

## Blind Spots Addressed

- Hidden assumptions: generated harnesses now require
  `Docs/Environment/ASSUMPTIONS.md`, and the evaluator warns when it lacks
  assumptions, limits, or verification steps.
- Stale manifests: the generated-harness evaluator now fails when
  `Docs/Environment/MANIFEST.md` lists files that do not exist.
- Fixture coverage: golden fixtures now include assumptions ledgers, and tests
  cover missing ledgers, weak ledgers, and broken manifest references.
- Claim calibration: README language now describes utility and limits without
  implying deterministic perfection.

## Remaining Opportunities

- Expand live sample-generation examples into higher-risk domains once safe
  synthetic briefs are available.
- Add per-domain fixture mutations for high-stakes domains such as security,
  legal, finance, hiring, and support.
- Add semantic-drift checks that compare local guidance against official docs,
  beyond the current official-source reachability check.
- Add a minimal deterministic bootstrap script for users who expect a CLI entry
  point before entering Codex.

## Utility Verdict

The project has real utility for repeatable Codex setup, especially when a team
wants subagents, skills, permissions, memory, and docs to work as one system.
Its value depends on maintaining the eval gate and keeping claims tied to what
the generated artifacts prove.

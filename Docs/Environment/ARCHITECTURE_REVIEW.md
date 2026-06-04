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
- Weak project-level evals: generated harnesses now require
  `Docs/Environment/EVAL_PLAN.md`, and the evaluator warns when the plan lacks
  success criteria, smoke checks, acceptance checks, reviewer checks, regression
  checks, or explicit verification/risk language.
- Thin self-improvement loop: generated harnesses now require
  `Docs/Environment/IMPROVEMENT_LOG.md`, with friction categories, seed
  patterns, an entry template, and an update rule that ties changes back to
  evidence and verification.
- Stale manifests: the generated-harness evaluator now fails when
  `Docs/Environment/MANIFEST.md` lists files that do not exist.
- Fixture coverage: golden fixtures now include assumptions ledgers, and tests
  cover missing ledgers, weak ledgers, and broken manifest references.
- High-risk domain coverage: generated-harness mutation tests now fail missing
  guardrails for security audit, legal research, financial analysis, hiring, and
  customer support scenarios.
- Semantic drift: a live maintainer check now compares core local Codex concepts
  against official OpenAI docs and records a review signal.
- Real usage evidence: a privacy-checked usage-record workflow now exists, and
  stricter validation flags can require successful non-synthetic records before
  maintainers make real-world usage claims. Current checked-in records are
  sanitized self-dogfood evidence from this public repo's Codex work; external
  reports now have a privacy-safe issue-template intake path.
- Claim calibration: README language now describes utility and limits without
  implying deterministic perfection.

## Remaining Opportunities

- Expand live sample-generation examples into more high-risk domains once safe
  synthetic briefs are available; security audit, legal research, financial
  modeling, hiring pipeline, and customer support now have public-safe task-trial
  fixtures.
- Add additional non-synthetic usage records through the privacy-checked
  recorder, especially external or multi-project records beyond the current
  self-dogfood evidence.
- Extend high-risk domain guardrail mutations as new bundled domains are added
  or official Codex safety guidance changes.
- Expand semantic drift checks from concept presence toward deeper schema-aware
  comparison as the official docs expose more stable machine-readable metadata.
- Keep the thin `scripts/codex_harness.py` wrapper aligned with the underlying
  scripts as workflows evolve, so users have one obvious first command without
  duplicating generator logic.

## Utility Verdict

The project has real utility for repeatable Codex setup, especially when a team
wants subagents, skills, permissions, memory, and docs to work as one system.
Its value depends on maintaining the eval gate and keeping claims tied to what
the generated artifacts prove.

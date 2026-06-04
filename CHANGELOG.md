# Changelog

All notable changes to the Codex Harness Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Added generated-harness fixture evaluation with scored categories for correctness, Codex compatibility, safety/privacy, user clarity, maintainability, and source alignment.
- Added generated-harness smoke checks with offline CI mode and optional live Codex CLI mode.
- Added five golden generated-harness fixtures: software development, knowledge work, security audit, nontechnical user, and multi-area hub.
- Added mutation tests for broken skill paths, missing skill metadata, missing agent registry targets, permission-profile gaps, hook drift, legacy paths, source-map gaps, and oversized AGENTS.md.
- Added `scripts/run_evals.py` as the local release gate and `.github/workflows/evals.yml` for pull request, push, scheduled, and manual eval runs.
- Added `Docs/Environment/CONTINUOUS_IMPROVEMENT.md` with the escaped-issue protocol.
- Added assumptions ledgers to generated-harness fixtures and evaluator coverage for missing or weak assumption records.
- Added manifest-reference validation so generated harness metadata fails when it points at files that are not on disk.
- Added `Docs/Environment/ARCHITECTURE_REVIEW.md` with a stress test of the project's assumptions, architecture, blind spots, and utility.
- Added `scripts/generate_minimal_harness.py` as a deterministic acceptance path that writes minimal valid Codex harnesses for software development, knowledge work, data analysis, and infrastructure profiles without requiring a live model run.
- Added `scripts/eval_deterministic_profiles.py` so the release gate explicitly generates, evaluates, and smokes every deterministic profile.
- Added `scripts/refresh_deterministic_examples.py` and checked-in deterministic example harnesses for each supported profile.
- Added `scripts/simulate_create_trigger.py` and contract tests for the deterministic `/create` preflight handoff artifact.
- Added `scripts/run_create_acceptance.py` for a deterministic preset `/create` acceptance flow that preserves trigger context, generates a harness, evaluates it, smokes it, and writes an acceptance report.
- Added `scripts/refresh_create_acceptance_examples.py` and a checked-in deterministic preset `/create` acceptance example.
- Added optional `python scripts/run_evals.py --codex-live` support for authenticated local Codex CLI live smoke checks.
- Added `Docs/Environment/PROOF_MATRIX.md` to map public claims to evidence artifacts, commands, proven scope, and remaining product-proof gaps.
- Added `scripts/capture_live_create_example.py` and `examples/live-create/README.md` for sanitized live `/create` capture packaging.
- Added a checked-in sanitized live `/create` capture and offline eval/smoke coverage for live-create examples.
- Added three checked-in sanitized live `/create` captures covering knowledge work, Python CLI, and data analysis.
- Added authenticated live example task trials to verify generated harnesses can steer Codex through representative work.

### Changed

- Strengthened the Codex port evaluator to validate source files, skill metadata, agent registry targets, config enum values, permission portability, hooks configuration, and network-policy consistency.
- Updated docs and templates to use current Codex paths and schema terms: `.agents/skills`, SKILL.md metadata, agent TOML, and permission-profile TOML.
- Updated README to clarify when the project is useful, when it is not, and what the eval gate actually proves.
- Updated generator and validation guidance to require ASSUMPTIONS, SOURCE_MAP, MANIFEST, and VALIDATION_REPORT records in generated harnesses.
- Updated live generated-harness smoke checks to use non-interactive `codex exec` instead of the interactive TUI path.

## [1.0.0] - 2026-06-01

Initial public release.

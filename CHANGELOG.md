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

### Changed

- Strengthened the Codex port evaluator to validate source files, skill metadata, agent registry targets, config enum values, permission portability, hooks configuration, and network-policy consistency.
- Updated docs and templates to use current Codex paths and schema terms: `.agents/skills`, SKILL.md metadata, agent TOML, and permission-profile TOML.
- Updated README to clarify when the project is useful, when it is not, and what the eval gate actually proves.
- Updated generator and validation guidance to require ASSUMPTIONS, SOURCE_MAP, MANIFEST, and VALIDATION_REPORT records in generated harnesses.

## [1.0.0] - 2026-06-01

Initial public release.

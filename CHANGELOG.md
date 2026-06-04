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

### Changed

- Strengthened the Codex port evaluator to validate source files, skill metadata, agent registry targets, config enum values, permission portability, hooks configuration, and network-policy consistency.
- Updated docs and templates to use current Codex paths and schema terms: `.agents/skills`, SKILL.md metadata, agent TOML, and permission-profile TOML.

## [1.0.0] - 2026-06-01

Initial public release.

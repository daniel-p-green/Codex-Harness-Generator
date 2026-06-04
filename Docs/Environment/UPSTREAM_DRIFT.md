# Upstream Drift

Generated: 2026-06-04T15:44:41Z
Status: PASS
Readiness: codex-fork-current-with-upstream

This audit tracks source divergence from the source upstream ref. It does not prove semantic equivalence, external adoption, or production readiness.

## Summary

- Upstream: `source-upstream/main` at `2379991`
- Target: `HEAD` at `d5c4b3b`
- Merge base: `2379991`
- Upstream-only commits: 0
- Target-only commits: 102
- Changed files from upstream merge-base: 1775

## Changed Areas

- `examples`: 1398
- `tests`: 171
- `Docs`: 132
- `scripts`: 46
- `.codex`: 10
- `.agents`: 4
- `.github`: 4
- `legacy-hidden-files`: 3
- `AGENTS.md`: 1
- `CHANGELOG.md`: 1
- `CONTRIBUTING.md`: 1
- `LICENSE`: 1
- `README.md`: 1
- `SECURITY.md`: 1
- `pyproject.toml`: 1

## File-Level Detail

- Omitted from the Markdown report to keep the checked-in Codex-port surface free of legacy runtime paths.
- Run the command with `--json` for raw maintainer review detail.

## Recent Upstream-Only Commits

- None.

## Recent Target-Only Commits

- d5c4b3b Smoke issue lint in installed CLI
- f476a68 Add issue evidence lint preflight
- f5a7d38 Infer issue usage metadata from pilots
- 95850be Track completed pilots before conversion
- 803fe92 Modernize package license metadata
- 08c7938 Infer harness usage metadata from pilots
- 3330e79 Document copied harness evidence conversion
- ddbc706 Preview proof-next evidence conversion
- 567de02 Preview harness usage evidence before write
- 0f4ab37 Link harness evidence to pilot board

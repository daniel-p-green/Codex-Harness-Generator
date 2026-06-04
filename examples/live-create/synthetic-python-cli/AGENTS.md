# AGENTS.md

These instructions apply to this synthetic Python CLI project unless a more specific instruction file overrides them.

## Project

This is a public-safe example CLI that scans local Markdown files, reports stale TODO items, and writes a concise cleanup summary. Treat all data, sample files, and reports as synthetic unless the user explicitly says otherwise.

## Working Defaults

- Prefer small, readable Python changes over framework-heavy solutions.
- Keep the CLI behavior explicit: inputs, date thresholds, output path, and exit codes should be easy to inspect.
- Read nearby code, tests, and docs before editing.
- Touch only files needed for the current task.
- Do not add network calls, background services, telemetry, or persistence outside the project without a clear request.
- Do not expose secrets, private notes, real user data, or machine-local paths in generated examples or reports.
- Preserve fake/public-safe wording in demos and docs.

## Implementation Guidance

- Use Python standard library modules when they are enough.
- Keep parsing deterministic for TODO extraction; use model judgment only for summaries or ambiguous cleanup advice.
- Prefer `pathlib`, typed helper functions, and narrow unit tests.
- Make stale TODO rules configurable but keep defaults obvious.
- Avoid broad rewrites of Markdown content unless the user asks for automated cleanup.

## Verification

- For behavior changes, run the narrowest relevant tests first.
- For CLI changes, verify at least one command invocation against synthetic Markdown fixtures.
- For reports, inspect the generated summary file and confirm it does not include private or absolute machine-local data.
- If a check cannot run, say exactly what was skipped and why.

## Security And Privacy

- Assume local Markdown may accidentally contain sensitive content; report only the minimum useful snippet.
- Redact obvious secrets such as tokens, credentials, keys, `.env` values, and private URLs.
- Keep file access inside the workspace unless the user explicitly authorizes another directory.
- Never send file contents to external services unless the user asks and the permission profile allows it.

## Task Routing

- Simple bug fix or CLI flag: inspect code, patch directly, run focused tests.
- TODO parsing or stale-date logic: use the `markdown-auditor` assistant for review or edge cases.
- Public demo data, report wording, or cleanup-summary shape: use the `summary-writer` assistant when helpful.
- Broad redesign: propose the smaller path first, then confirm scope before changing architecture.

## Done Means

The change is implemented, verified with tests or a concrete CLI run, and any remaining risk is called out plainly.

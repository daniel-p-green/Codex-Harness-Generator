# Assumptions

- Assumption: the target project is a synthetic Python CLI example, not a real private codebase.
- Assumption: Markdown TODO input data is public-safe fake data for demonstration.
- Assumption: no external services are needed to scan local files or write summaries.
- Assumption: the user prefers a compact harness over a broad multi-assistant environment.

## Limits

- This harness does not implement the CLI itself.
- This harness does not validate any future project source files until they exist.
- Permission patterns reduce accidental exposure but cannot replace reviewing generated public artifacts.

## Verify

When project code is added, verify the harness by asking Codex to inspect the CLI, run focused tests, and execute one synthetic scan command.

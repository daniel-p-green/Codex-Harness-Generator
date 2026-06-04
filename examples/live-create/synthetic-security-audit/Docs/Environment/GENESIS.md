# Genesis

## Project Summary

Synthetic security audit workspace for public-safe code review examples. The
example is intentionally small and uses fake vulnerable snippets seeded during
task trials.

## User Context

- Experience level: intermediate
- Work-area shape: one focused area
- Generation mode: public-safe high-risk task-trial fixture
- Data sensitivity: synthetic only
- External services: none requested

## Work Types

- Inspect local synthetic source files for security risks.
- Write evidence-backed security review notes.
- Separate exploitability assumptions from verified local evidence.
- Recommend safe remediation without payloads or active testing.

## Constraints

- Do not inspect real secrets, tokens, credentials, private keys, or `.env`
  files.
- Do not run exploit code, scanners, destructive commands, network probes, or
  active testing without explicit authorization.
- Keep findings defensive and source-backed.

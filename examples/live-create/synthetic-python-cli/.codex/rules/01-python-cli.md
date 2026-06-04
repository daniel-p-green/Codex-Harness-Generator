# Python CLI Rule

Use simple, maintainable Python.

- Prefer the standard library for scanning Markdown, parsing dates, writing files, and formatting output.
- Keep command-line options explicit and documented.
- Use `pathlib.Path` for paths and avoid stringly path joins.
- Put parsing logic in testable functions, not only in command handlers.
- Avoid hidden network access, telemetry, daemon processes, or global machine writes.
- Fail loud with clear messages for missing paths, invalid thresholds, and unwritable output files.

Verification should include focused tests and at least one synthetic CLI invocation when behavior changes.

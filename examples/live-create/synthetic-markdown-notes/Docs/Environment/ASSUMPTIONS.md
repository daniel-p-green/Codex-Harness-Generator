# Assumptions

## Assumptions

- All project data is synthetic and public-safe.
- The workspace is one focused area, not a multi-area setup.
- Markdown outputs are sufficient for the proof run.
- No external connectors are required.

## Limits

- The harness does not process real sensitive data.
- It does not directly access web-based document tools.
- It does not install or depend on MarkItDown, Pandoc, or any MCP server.
- Public-safety checks are advisory, not a deterministic compliance system.

## Verify

- Run `python scripts/eval_generated_harness.py temporary synthetic target` from the generator repository.
- Run `python scripts/smoke_generated_harness.py temporary synthetic target` from the generator repository.
- Run `/health-check` inside the target for an in-workspace check.

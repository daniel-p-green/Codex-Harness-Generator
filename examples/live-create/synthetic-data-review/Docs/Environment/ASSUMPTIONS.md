# Assumptions

## Assumptions

- The workspace uses synthetic CSV data only.
- The user is comfortable with basic terminal and file paths.
- Weekly metrics can be computed from local CSV exports.
- No external services or live connectors are required.

## Known Limits

- Metric formulas beyond defaults must be confirmed before use.
- Standard-library CSV scripts are intentionally lightweight and may need extension for very large files.
- Public-safe status depends on keeping real identifiers out of future inputs.

## Verify

- Run the generated quality-check script against a sample CSV before relying on a new workflow.
- Confirm date columns and week windows before publishing weekly notes.
- Re-run validation after changing rules, skills, agents, or config.


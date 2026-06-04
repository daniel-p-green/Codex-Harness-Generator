# Error Handling

- Fail loud on CSV parse errors, missing date columns, empty result sets, and undefined metrics.
- Report the smallest reproducible cause: file path, command, row/column if available, and observed error.
- Do not smooth over contradictory counts; re-run the deterministic check and identify which input changed.
- If a chart note cannot be traced to computed data, mark it as a draft claim and ask for confirmation.
- Keep partial outputs only when they are labeled as partial.


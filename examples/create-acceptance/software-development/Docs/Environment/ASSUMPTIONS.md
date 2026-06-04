# Assumptions

- Assumption: This deterministic harness targets a small Python CLI utility for a solo developer.
- Assumption: The project has local files that can be inspected before edits.
- Assumption: The narrowest meaningful check is usually a unit test or CLI command.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/run-harness-evals.py` locally, or run `codex-harness validate <target>` from the generator repo.

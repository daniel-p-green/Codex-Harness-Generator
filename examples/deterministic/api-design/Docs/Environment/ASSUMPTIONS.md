# Assumptions

- Assumption: This deterministic harness targets local API design artifacts and examples.
- Assumption: API contracts should stay source-backed and compatible with documented clients.
- Assumption: Verification means checking examples, schemas, and compatibility notes.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/run-harness-evals.py` locally, or run `codex-harness validate <target>` from the generator repo.

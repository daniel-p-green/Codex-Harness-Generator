# Assumptions

- Assumption: This deterministic harness targets local infrastructure files and runbooks.
- Assumption: Destructive commands need explicit user approval and rollback context.
- Assumption: Verification should prefer dry-run or validation commands when available.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.

# Assumptions

- Assumption: This deterministic harness targets local product planning artifacts.
- Assumption: Product decisions should cite user evidence or explicit assumptions.
- Assumption: Verification means checking acceptance criteria, source notes, scope, and tradeoffs.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.

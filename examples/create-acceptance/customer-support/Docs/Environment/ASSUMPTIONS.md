# Assumptions

- Assumption: This deterministic harness targets support documentation and support-ops artifacts.
- Assumption: Customer-facing facts require source grounding and owner approval for commitments.
- Assumption: Verification means checking sources, privacy, PII, escalation, and draft boundaries.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.

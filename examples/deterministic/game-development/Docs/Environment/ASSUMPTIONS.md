# Assumptions

- Assumption: This deterministic harness targets local game project files and docs.
- Assumption: Binary assets and project settings can be fragile and need conservative handling.
- Assumption: Verification means build, scene, test, or manual playtest evidence where possible.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/check-harness.py` locally, or run `codex-harness validate <target>` from the generator repo.

# Beta Exit Audit

Generated: 2026-06-05T00:14:30Z
Status: PASS
Readiness: beta-exit-ready-for-final-gate

This audit reports beta-exit readiness; it does not itself prove external adoption or replace proof-status --beta-exit.

## Criteria

| Criterion | Status | Detail | Command |
|---|---|---|---|
| `non_synthetic_usage_records` | PASS | 8/5 valid usage records | `codex-harness usage-gaps` |
| `external_or_multi_project_records` | PASS | 3/3 external or multi-project records | `codex-harness usage-gaps` |
| `distinct_domains` | PASS | 7/4 distinct domains | `codex-harness usage-gaps` |
| `installed_brief_generation` | PASS | 3/2 installed brief-based generation records | `codex-harness usage-gaps` |
| `source_freshness` | PASS | Docs/Environment/SOURCE_FRESHNESS.md status=pass | `codex-harness source-freshness` |
| `semantic_alignment` | PASS | Docs/Environment/SEMANTIC_ALIGNMENT.md status=pass | `codex-harness semantic-alignment` |
| `release_gate` | PASS | Docs/Environment/eval-history/20260605T000641Z-beta-exit-offline.json status=pass generated=2026-06-05T00:06:41Z label=beta-exit-offline passed=24 failed=0 steps=24 | `codex-harness gate` |
| `beta_exit_proof_status` | PASS | Docs/Environment/PROOF_STATUS.md status=pass mode=beta-exit readiness=Beta exit proof complete | `codex-harness proof-status --beta-exit` |

## Current Evidence

- Usage records: 8
- External or multi-project records: 3
- Distinct domains: 7
- Installed brief-based generation records: 3
- Pending pilots: 3
- Completed but not converted pilots: 0
- Converted pilots with validated usage records: 0

## Remaining Usage Gaps

- Usage records: 0
- External or multi-project records: 0
- Distinct domains: 0
- Installed brief-based generation records: 0

## Next Actions

- Beta-exit usage thresholds are satisfied; run proof-status with beta-exit thresholds before changing the README status.

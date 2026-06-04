# Beta Exit Audit

Generated: 2026-06-04T23:50:19Z
Status: PASS
Readiness: missing-beta-exit-evidence

This audit reports beta-exit readiness; it does not itself prove external adoption or replace proof-status --beta-exit.

## Criteria

| Criterion | Status | Detail | Command |
|---|---|---|---|
| `non_synthetic_usage_records` | PASS | 5/5 valid usage records | `codex-harness usage-gaps` |
| `external_or_multi_project_records` | MISSING | 0/3 external or multi-project records | `codex-harness usage-gaps` |
| `distinct_domains` | PASS | 4/4 distinct domains | `codex-harness usage-gaps` |
| `installed_brief_generation` | PASS | 3/2 installed brief-based generation records | `codex-harness usage-gaps` |
| `source_freshness` | PASS | Docs/Environment/SOURCE_FRESHNESS.md status=pass | `codex-harness source-freshness` |
| `semantic_alignment` | PASS | Docs/Environment/SEMANTIC_ALIGNMENT.md status=pass | `codex-harness semantic-alignment` |
| `release_gate` | MISSING | Run locally and on CI before dropping the beta label. | `codex-harness gate` |
| `beta_exit_proof_status` | MISSING | Run after usage thresholds and source checks are satisfied. | `codex-harness proof-status --beta-exit` |

## Current Evidence

- Usage records: 5
- External or multi-project records: 0
- Distinct domains: 4
- Installed brief-based generation records: 3
- Pending pilots: 3
- Completed but not converted pilots: 0
- Converted pilots with validated usage records: 0

## Remaining Usage Gaps

- Usage records: 0
- External or multi-project records: 3
- Distinct domains: 0
- Installed brief-based generation records: 0

## Next Actions

- Collect 3 more external or multi-project usage record(s).
- For the next suggested pilot, run `codex-harness prepare-next-pilot <target> --pilot-record-dir Docs/Environment/pilot-records` or copy the suggested `codex-harness prepare-pilot <target> --pilot-record-dir Docs/Environment/pilot-records` command, review the generated pack, track it with `codex-harness pilot-board`, update status with `codex-harness pilot-update`, then convert completed evidence with `usage-from-harness` or `usage-from-issue`.

# Proof Status

Generated: 2026-06-04T19:46:03Z
Status: PASS
Mode: self-dogfood-proof
Readiness: Codex-equivalent beta with checked-in self-dogfood proof

This report summarizes checked-in evidence. It is intentionally
conservative and should be read with `PROOF_MATRIX.md`.

## Checks

| Check | Status | Detail |
|---|---|---|
| `proof_matrix` | PASS | Docs/Environment/PROOF_MATRIX.md |
| `equivalence_matrix` | PASS | Docs/Environment/CODEX_EQUIVALENCE_MATRIX.md |
| `usage_report` | PASS | Docs/Environment/USAGE_RECORDS.md |
| `external_usage_issue_example` | PASS | Docs/Environment/EXTERNAL_USAGE_ISSUE_EXAMPLE.md |
| `usage_gaps_report` | PASS | Docs/Environment/USAGE_GAPS.md |
| `pilot_campaign_report` | PASS | Docs/Environment/PILOT_CAMPAIGN.md |
| `pilot_board_report` | PASS | Docs/Environment/PILOT_BOARD.md |
| `pilot_outreach_report` | PASS | Docs/Environment/PILOT_OUTREACH.md |
| `pilot_handoff_audit_report` | PASS | Docs/Environment/PILOT_HANDOFF_AUDIT.md |
| `pilot_github_issues_report` | PASS | Docs/Environment/PILOT_GITHUB_ISSUES.md |
| `pilot_github_sync_report` | PASS | Docs/Environment/PILOT_GITHUB_SYNC.md |
| `pilot_next_action_report` | PASS | Docs/Environment/PILOT_NEXT_ACTION.md |
| `pilot_github_followups` | PASS | followups=0 comment_commands=0 |
| `proof_next_report` | PASS | Docs/Environment/PROOF_NEXT.md |
| `beta_exit_audit_report` | PASS | Docs/Environment/BETA_EXIT_AUDIT.md |
| `upstream_drift_report` | PASS | Docs/Environment/UPSTREAM_DRIFT.md |
| `source_freshness_report` | PASS | report=Docs/Environment/SOURCE_FRESHNESS.md status=pass json_status=pass generated=2026-06-04T11:50:18Z |
| `semantic_alignment_report` | PASS | report=Docs/Environment/SEMANTIC_ALIGNMENT.md status=pass json_status=pass generated=2026-06-04T11:50:18Z |
| `task_trials_report` | PASS | examples/live-create/TASK_TRIALS.md |
| `checked_in_example_inventory` | PASS | profiles=20 brief_examples=4 failures=0 |
| `installable_cli` | PASS | profiles=20 doctor=pass init=pass quickstart=pass prepare_pilot=pass init_from_project=pass demo_capture=pass validate=pass inspect=pass adoption_plan=pass equivalence=pass upstream_drift=pass local_eval=pass public_usage_report=pass evidence_packet=pass pilot_pack=pass usage_from_harness=pass usage_from_issue_lint=pass usage_from_issue_preview=pass usage_from_issue=pass usage_from_github_issue_lint=pass prepare_next_pilot=pass prepare_pilot_batch=pass pilot_board=pass pilot_update=pass pilot_outreach=pass pilot_handoff=pass pilot_handoff_audit=pass pilot_github_issues=pass pilot_github_sync=pass pilot_next_action=pass usage_from_issue_pilot_conversion=pass usage_gaps=pass beta_exit_audit=pass pilot_campaign=pass proof_next=pass migration_audit=pass prepare_migration=pass eval=pass |
| `live_task_trials` | PASS | 8/8 pass; required >= 8 |
| `non_synthetic_usage` | PASS | records=2 non_synthetic=2 success=2 external_or_multi_project=0 domains=1 installed_brief_generation=0 |

## Usage Evidence

- Total records: 2
- Non-synthetic records: 2
- Successful records: 2
- External or multi-project records: 0
- Distinct domains: 1
- Installed brief-based generation records: 0

## What This Does Not Prove

- Broad external adoption.
- Longitudinal performance across many private repos.
- Every future live model-mediated /create run will be ideal.
- Organization-level compliance, policy enforcement, or production security controls.

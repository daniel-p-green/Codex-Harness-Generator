# Beta Status

Generated: 2026-06-04T23:32:08Z
Status: PASS
Readiness: missing-beta-exit-evidence

This status report is an operator dashboard. It is not usage proof; only converted, validated usage records count toward beta exit.

## Evidence Gap

- Usage records: 2 total; 3 still needed
- External or multi-project records: 0 current; 3 still needed
- Distinct domains: 1 current; 3 still needed
- Installed brief-based generation records: 0 current; 2 still needed

## Pilot Queue

- Pilot readiness: waiting-for-reporters
- Live issues: 3
- Waiting for reporter: 3
- Conversion ready: 0
- Reporter replies: 0
- Stale follow-ups: 0
- Next reminder review: `2026-06-07T19:38:17Z`

Missing fields across waiting issues:

- `evidence`: 3
- `limitations`: 3
- `outcome`: 3
- `privacy_review`: 3
- `task_summary`: 3
- `verification`: 3

## Next Action

- Type: `wait-for-reporter-response`
- Priority: `medium`
- Pilot: `llm-app-pilot`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3
- Reason: A maintainer follow-up is already posted; wait for reporter evidence, then rerun sync.

```bash
codex-harness pilot-github-sync --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --usage-report Docs/Environment/USAGE_RECORDS.md --pilot-board-report Docs/Environment/PILOT_BOARD.md --report Docs/Environment/PILOT_GITHUB_SYNC.md --followup-dir Docs/Environment/pilot-github-followups --repo daniel-p-green/Codex-Harness-Generator
```

## Commands

### next live pilot action

A maintainer follow-up is already posted; wait for reporter evidence, then rerun sync.

```bash
codex-harness pilot-github-sync --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --usage-report Docs/Environment/USAGE_RECORDS.md --pilot-board-report Docs/Environment/PILOT_BOARD.md --report Docs/Environment/PILOT_GITHUB_SYNC.md --followup-dir Docs/Environment/pilot-github-followups --repo daniel-p-green/Codex-Harness-Generator
```

### refresh live pilot sync

refresh public pilot issue state before converting reporter evidence.

```bash
codex-harness pilot-github-sync --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --usage-report Docs/Environment/USAGE_RECORDS.md --pilot-board-report Docs/Environment/PILOT_BOARD.md --report Docs/Environment/PILOT_GITHUB_SYNC.md --followup-dir Docs/Environment/pilot-github-followups --repo daniel-p-green/Codex-Harness-Generator
```

### refresh usage gaps

refresh the evidence thresholds before changing beta-readiness claims.

```bash
codex-harness usage-gaps --record-dir Docs/Environment/usage-records
```

### refresh proof next

refresh the ordered beta-exit evidence collection checklist.

```bash
codex-harness proof-next --record-dir Docs/Environment/usage-records --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --usage-report Docs/Environment/USAGE_RECORDS.md --pilot-github-sync-report Docs/Environment/PILOT_GITHUB_SYNC.md --pilot-github-followup-dir Docs/Environment/pilot-github-followups
```

### strict beta-exit doctor

apply the roadmap usage-evidence thresholds before treating the repo as beta-exit ready.

```bash
codex-harness doctor --beta-exit --record-dir Docs/Environment/usage-records
```

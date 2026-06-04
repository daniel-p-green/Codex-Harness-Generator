# Pilot GitHub Issue Sync

Generated: 2026-06-04T18:41:35Z
Status: PASS
Readiness: waiting-for-reporters

Pilot GitHub issue sync checks public intake readiness only; it is not usage proof until completed evidence is converted into a validated usage record.

## Summary

- Tracked pilots: 3
- Live issue URLs: 3
- Conversion-ready issues: 0
- Waiting for reporter: 3
- Needs attention: 0
- Missing live issue URL: 0

## Issue Readiness

### llm-app-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3
- GitHub state: `OPEN`
- Comments included: 0
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations

Errors:
- Missing required issue field(s): outcome, task_summary, evidence, verification, privacy_review, limitations
- Non-synthetic usage requires at least two evidence bullets
- Non-synthetic usage requires at least two verification bullets
- Non-synthetic usage requires at least one limitation

Commands:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

### security-audit-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1
- GitHub state: `OPEN`
- Comments included: 0
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations

Errors:
- Missing required issue field(s): outcome, task_summary, evidence, verification, privacy_review, limitations
- Non-synthetic usage requires at least two evidence bullets
- Non-synthetic usage requires at least two verification bullets
- Non-synthetic usage requires at least one limitation

Commands:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

### customer-support-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2
- GitHub state: `OPEN`
- Comments included: 0
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations

Errors:
- Missing required issue field(s): outcome, task_summary, evidence, verification, privacy_review, limitations
- Non-synthetic usage requires at least two evidence bullets
- Non-synthetic usage requires at least two verification bullets
- Non-synthetic usage requires at least one limitation

Commands:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

## Claim Boundary

Do not count live issues, comments, or passing lint as adoption proof. Count only converted, validated usage records.

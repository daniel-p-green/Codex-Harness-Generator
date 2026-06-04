# Pilot GitHub Issue Sync

Generated: 2026-06-04T23:14:41Z
Status: PASS
Readiness: waiting-for-reporters

Pilot GitHub issue sync checks public intake readiness only; it is not usage proof until completed evidence is converted into a validated usage record.

## Summary

- Tracked pilots: 3
- Live issue URLs: 3
- Conversion-ready issues: 0
- Waiting for reporter: 3
- Maintainer follow-ups already posted: 3
- Stale maintainer follow-ups: 3
- GitHub comments fetched: 6
- Maintainer/automation comments excluded: 6
- Reporter replies: 0
- Reporter replies after latest maintainer follow-up: 0
- Follow-up reminders due: 0
- Reminder review threshold: 72.0 hours
- Needs attention: 0
- Missing live issue URL: 0

## Issue Readiness

### llm-app-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3
- GitHub state: `OPEN`
- GitHub comments fetched: 2
- Reporter comments included: 0
- Maintainer/automation comments excluded: 2
- Maintainer follow-up already posted: `true`
- Maintainer follow-up stale: `true`
- Maintainer follow-up URL: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3#issuecomment-4625495059
- Maintainer follow-up posted at: `2026-06-04T19:38:17Z`
- Maintainer follow-up age: `3.61` hours
- Reminder due: `false`
- Next reminder review at: `2026-06-07T19:38:17Z`
- Reporter replies: 0
- Latest reporter reply: none
- Reporter replied after latest maintainer follow-up: `false`
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations
- Follow-up file: `Docs/Environment/pilot-github-followups/llm-app-pilot-followup.md`
- Follow-up action: edit existing follow-up comment with refreshed template

Errors:
- Missing required issue field(s): outcome, task_summary, evidence, verification, privacy_review, limitations
- Non-synthetic usage requires at least two evidence bullets
- Non-synthetic usage requires at least two verification bullets
- Non-synthetic usage requires at least one limitation

Commands:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --no-write --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --json
gh api --method PATCH /repos/daniel-p-green/Codex-Harness-Generator/issues/comments/4625495059 --raw-field body="$(cat Docs/Environment/pilot-github-followups/llm-app-pilot-followup.md)"
```

Reporter follow-up:

```markdown
Maintainer follow-up already posted, but the generated template has changed; edit the existing follow-up comment with the refreshed file instead of posting a duplicate.
```

### security-audit-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1
- GitHub state: `OPEN`
- GitHub comments fetched: 2
- Reporter comments included: 0
- Maintainer/automation comments excluded: 2
- Maintainer follow-up already posted: `true`
- Maintainer follow-up stale: `true`
- Maintainer follow-up URL: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1#issuecomment-4625495203
- Maintainer follow-up posted at: `2026-06-04T19:38:18Z`
- Maintainer follow-up age: `3.61` hours
- Reminder due: `false`
- Next reminder review at: `2026-06-07T19:38:18Z`
- Reporter replies: 0
- Latest reporter reply: none
- Reporter replied after latest maintainer follow-up: `false`
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations
- Follow-up file: `Docs/Environment/pilot-github-followups/security-audit-pilot-followup.md`
- Follow-up action: edit existing follow-up comment with refreshed template

Errors:
- Missing required issue field(s): outcome, task_summary, evidence, verification, privacy_review, limitations
- Non-synthetic usage requires at least two evidence bullets
- Non-synthetic usage requires at least two verification bullets
- Non-synthetic usage requires at least one limitation

Commands:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --no-write --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --json
gh api --method PATCH /repos/daniel-p-green/Codex-Harness-Generator/issues/comments/4625495203 --raw-field body="$(cat Docs/Environment/pilot-github-followups/security-audit-pilot-followup.md)"
```

Reporter follow-up:

```markdown
Maintainer follow-up already posted, but the generated template has changed; edit the existing follow-up comment with the refreshed file instead of posting a duplicate.
```

### customer-support-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2
- GitHub state: `OPEN`
- GitHub comments fetched: 2
- Reporter comments included: 0
- Maintainer/automation comments excluded: 2
- Maintainer follow-up already posted: `true`
- Maintainer follow-up stale: `true`
- Maintainer follow-up URL: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2#issuecomment-4625495326
- Maintainer follow-up posted at: `2026-06-04T19:38:19Z`
- Maintainer follow-up age: `3.61` hours
- Reminder due: `false`
- Next reminder review at: `2026-06-07T19:38:19Z`
- Reporter replies: 0
- Latest reporter reply: none
- Reporter replied after latest maintainer follow-up: `false`
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations
- Follow-up file: `Docs/Environment/pilot-github-followups/customer-support-pilot-followup.md`
- Follow-up action: edit existing follow-up comment with refreshed template

Errors:
- Missing required issue field(s): outcome, task_summary, evidence, verification, privacy_review, limitations
- Non-synthetic usage requires at least two evidence bullets
- Non-synthetic usage requires at least two verification bullets
- Non-synthetic usage requires at least one limitation

Commands:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --no-write --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --repo daniel-p-green/Codex-Harness-Generator --json
gh api --method PATCH /repos/daniel-p-green/Codex-Harness-Generator/issues/comments/4625495326 --raw-field body="$(cat Docs/Environment/pilot-github-followups/customer-support-pilot-followup.md)"
```

Reporter follow-up:

```markdown
Maintainer follow-up already posted, but the generated template has changed; edit the existing follow-up comment with the refreshed file instead of posting a duplicate.
```

## Claim Boundary

Do not count live issues, comments, or passing lint as adoption proof. Count only converted, validated usage records.

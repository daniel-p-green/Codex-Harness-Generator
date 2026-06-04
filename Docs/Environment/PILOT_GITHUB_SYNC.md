# Pilot GitHub Issue Sync

Generated: 2026-06-04T19:34:36Z
Status: PASS
Readiness: waiting-for-reporters

Pilot GitHub issue sync checks public intake readiness only; it is not usage proof until completed evidence is converted into a validated usage record.

## Summary

- Tracked pilots: 3
- Live issue URLs: 3
- Conversion-ready issues: 0
- Waiting for reporter: 3
- Maintainer follow-ups already posted: 0
- Needs attention: 0
- Missing live issue URL: 0

## Issue Readiness

### llm-app-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3
- GitHub state: `OPEN`
- Comments included: 0
- Maintainer follow-up already posted: `false`
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations
- Follow-up file: `Docs/Environment/pilot-github-followups/llm-app-pilot-followup.md`

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
gh issue comment https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --body-file Docs/Environment/pilot-github-followups/llm-app-pilot-followup.md
```

Reporter follow-up:

```markdown
<!-- codex-harness-maintainer-followup -->

Thanks for taking this on. The issue is not ready to convert into usage evidence yet.

Please reply with the missing public-safe sections below. Keep the report free of secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.

### Outcome

Use `success`, `partial`, `failed`, or `inconclusive`.

### Public-safe task summary

Summarize one real task in public-safe terms without private repo names, secrets, personal data, raw logs, or proprietary source.

### Evidence

Add at least two public-safe bullets about what the generated harness helped you do or verify.

### Verification performed

Add at least two bullets naming the checks you actually ran or reviews you performed.

### Privacy review

State that the report excludes secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.

### Limitations

Add at least one bullet describing the scope limit, such as one task, one repo, one reporter, or incomplete coverage.

Once those sections are present, a maintainer can run `codex-harness pilot-github-sync` again and preview conversion.
```

### security-audit-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1
- GitHub state: `OPEN`
- Comments included: 0
- Maintainer follow-up already posted: `false`
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations
- Follow-up file: `Docs/Environment/pilot-github-followups/security-audit-pilot-followup.md`

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
gh issue comment https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --body-file Docs/Environment/pilot-github-followups/security-audit-pilot-followup.md
```

Reporter follow-up:

```markdown
<!-- codex-harness-maintainer-followup -->

Thanks for taking this on. The issue is not ready to convert into usage evidence yet.

Please reply with the missing public-safe sections below. Keep the report free of secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.

### Outcome

Use `success`, `partial`, `failed`, or `inconclusive`.

### Public-safe task summary

Summarize one real task in public-safe terms without private repo names, secrets, personal data, raw logs, or proprietary source.

### Evidence

Add at least two public-safe bullets about what the generated harness helped you do or verify.

### Verification performed

Add at least two bullets naming the checks you actually ran or reviews you performed.

### Privacy review

State that the report excludes secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.

### Limitations

Add at least one bullet describing the scope limit, such as one task, one repo, one reporter, or incomplete coverage.

Once those sections are present, a maintainer can run `codex-harness pilot-github-sync` again and preview conversion.
```

### customer-support-pilot

- Pilot status: `invited`
- Readiness: `waiting-for-reporter`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2
- GitHub state: `OPEN`
- Comments included: 0
- Maintainer follow-up already posted: `false`
- Missing fields: outcome, task_summary, evidence, verification, privacy_review, limitations
- Follow-up file: `Docs/Environment/pilot-github-followups/customer-support-pilot-followup.md`

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
gh issue comment https://github.com/daniel-p-green/Codex-Harness-Generator/issues/2 --body-file Docs/Environment/pilot-github-followups/customer-support-pilot-followup.md
```

Reporter follow-up:

```markdown
<!-- codex-harness-maintainer-followup -->

Thanks for taking this on. The issue is not ready to convert into usage evidence yet.

Please reply with the missing public-safe sections below. Keep the report free of secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.

### Outcome

Use `success`, `partial`, `failed`, or `inconclusive`.

### Public-safe task summary

Summarize one real task in public-safe terms without private repo names, secrets, personal data, raw logs, or proprietary source.

### Evidence

Add at least two public-safe bullets about what the generated harness helped you do or verify.

### Verification performed

Add at least two bullets naming the checks you actually ran or reviews you performed.

### Privacy review

State that the report excludes secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.

### Limitations

Add at least one bullet describing the scope limit, such as one task, one repo, one reporter, or incomplete coverage.

Once those sections are present, a maintainer can run `codex-harness pilot-github-sync` again and preview conversion.
```

## Claim Boundary

Do not count live issues, comments, or passing lint as adoption proof. Count only converted, validated usage records.

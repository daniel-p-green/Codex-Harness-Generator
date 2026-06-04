# Pilot GitHub Issue Queue

Generated: 2026-06-04T18:17:14Z
Status: PASS
Readiness: github-issue-ready

GitHub issue drafts help open public pilot intake issues; they are not usage proof until a real task is completed, privacy-reviewed, and converted into a validated usage record.

## Summary

- GitHub-ready issue bodies: 3
- Included statuses: prepared, invited, completed
- Pilot board readiness: pilot-funnel-active

## Issue Commands

### 1. External usage pilot: LLM app pilot (`llm-app-pilot`)

- Status: `prepared`
- Domain: LLM app
- Source type: `external`
- Generation path: `installed-quickstart`
- Body file: `Docs/Environment/pilot-github-issues/llm-app-pilot-github-issue.md`

Create public issue:

```bash
gh issue create --title 'External usage pilot: LLM app pilot' --body-file Docs/Environment/pilot-github-issues/llm-app-pilot-github-issue.md
```

Then mark the pilot invited:

```bash
codex-harness pilot-update llm-app-pilot --status invited --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "sent to reporter"
```

Preview the incomplete issue body before sending if desired:

```bash
codex-harness usage-from-issue Docs/Environment/pilot-github-issues/llm-app-pilot-github-issue.md --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue Docs/Environment/pilot-github-issues/llm-app-pilot-github-issue.md --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

After the reporter completes the public issue, lint, preview, and convert from GitHub:

```bash
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

### 2. External usage pilot: security audit pilot (`security-audit-pilot`)

- Status: `prepared`
- Domain: security audit
- Source type: `external`
- Generation path: `installed-quickstart`
- Body file: `Docs/Environment/pilot-github-issues/security-audit-pilot-github-issue.md`

Create public issue:

```bash
gh issue create --title 'External usage pilot: security audit pilot' --body-file Docs/Environment/pilot-github-issues/security-audit-pilot-github-issue.md
```

Then mark the pilot invited:

```bash
codex-harness pilot-update security-audit-pilot --status invited --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "sent to reporter"
```

Preview the incomplete issue body before sending if desired:

```bash
codex-harness usage-from-issue Docs/Environment/pilot-github-issues/security-audit-pilot-github-issue.md --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue Docs/Environment/pilot-github-issues/security-audit-pilot-github-issue.md --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

After the reporter completes the public issue, lint, preview, and convert from GitHub:

```bash
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

### 3. External usage pilot: customer support pilot (`customer-support-pilot`)

- Status: `prepared`
- Domain: customer support
- Source type: `external`
- Generation path: `installed-quickstart`
- Body file: `Docs/Environment/pilot-github-issues/customer-support-pilot-github-issue.md`

Create public issue:

```bash
gh issue create --title 'External usage pilot: customer support pilot' --body-file Docs/Environment/pilot-github-issues/customer-support-pilot-github-issue.md
```

Then mark the pilot invited:

```bash
codex-harness pilot-update customer-support-pilot --status invited --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "sent to reporter"
```

Preview the incomplete issue body before sending if desired:

```bash
codex-harness usage-from-issue Docs/Environment/pilot-github-issues/customer-support-pilot-github-issue.md --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue Docs/Environment/pilot-github-issues/customer-support-pilot-github-issue.md --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

After the reporter completes the public issue, lint, preview, and convert from GitHub:

```bash
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-github-issue <issue-number-or-url> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

## Claim Boundary

Opening an issue or marking a pilot invited is not adoption evidence. Count only completed, privacy-reviewed task evidence converted into valid usage records.

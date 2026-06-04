# External Usage Pilot: customer support pilot

GitHub issue drafts help open public pilot intake issues; they are not usage proof until a real task is completed, privacy-reviewed, and converted into a validated usage record.

## Reporter Instructions

Would you be willing to try one small real Codex task using customer support pilot?

- Domain: customer support
- Pilot pack: Docs/Environment/beta-exit-pilot-materials/customer-support-pilot-pilot-pack.md
- Issue draft: Docs/Environment/beta-exit-pilot-materials/customer-support-pilot-usage-issue.md

Please pick one privacy-safe task, run the generated harness checks, record the task trial,
and share either the completed issue draft or a private copied harness directory with public-safe evidence.

Do not include secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.
A private-summary report is fine if the raw evidence cannot be public.

After completing one privacy-safe task, reply to this issue with the completion template below. Maintainers can then run `codex-harness usage-from-github-issue ... --include-comments` without asking you to edit the original issue body.
Keep evidence public-safe: no secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.

## Reporter Completion Reply Template

Copy this section into a new issue comment after the pilot task, then replace the guidance text with your public-safe result.

```markdown
### Outcome

success

### Public-safe task summary

Describe one real task you completed with this generated harness. Keep it public-safe.

### Evidence

- Evidence item 1: what the harness helped produce, organize, catch, or verify.
- Evidence item 2: another public-safe artifact, workflow improvement, or observed behavior.

### Verification performed

- Check 1: command, generated script, review step, or artifact inspection you actually performed.
- Check 2: second check or review that supports the outcome.

### Privacy review

This report excludes secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, and raw private transcripts.

### Limitations

- This reports one generated harness on one task; it does not prove broad adoption or production readiness.
```

## Maintainer Preview Commands

```bash
codex-harness usage-from-issue <this-issue-body.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue <this-issue-body.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

## Usage Report Body

### Pilot or usage-record slug

customer-support-pilot

### Domain or project type

customer support

### Generated harness profile or label

Customer Support Workspace Pilot

### Evidence type

private-summary

### Source type

external

### Generation path

installed-quickstart

### Outcome

_no response_

### Public-safe task summary

_no response_

### Evidence

_no response_

### Verification performed

_no response_

### Privacy review

_no response_

### Limitations

_no response_

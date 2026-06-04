# Reporter Completion Reply: llm-app-pilot

Copy the Markdown below into a new GitHub issue comment after completing one real, public-safe task with the generated harness.

Do not include secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, or raw private transcripts.

- Pilot: `llm-app-pilot`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3
- Domain: LLM app

## Reply Template

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

## Maintainer Validation

After the reporter posts this reply, rerun live sync or preview conversion before writing usage evidence:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

This reply is not usage proof until it passes lint and is converted into a validated usage record.

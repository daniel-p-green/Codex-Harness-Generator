# Reporter Completion Reply: security-audit-pilot

Copy the Markdown below into a new GitHub issue comment after completing one real, public-safe task with the generated harness.

Do not include secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, or raw private transcripts.

- Pilot: `security-audit-pilot`
- Issue: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1
- Domain: security audit

## Reply Template

```markdown
### Outcome

_no response_
<!-- Use `success`, `partial`, `failed`, or `inconclusive`. -->

### Public-safe task summary

_no response_
<!-- Describe one real task you completed with this generated harness. Keep it public-safe. -->

### Evidence

_no response_
<!-- Add at least two public-safe bullets about what the harness helped produce, organize, catch, or verify. -->

### Verification performed

_no response_
<!-- Add at least two bullets naming commands, generated scripts, review steps, or artifact inspections you actually performed. -->

### Privacy review

_no response_
<!-- State that the report excludes secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, and raw private transcripts. -->

### Limitations

_no response_
<!-- Add at least one bullet describing the scope limit, such as one generated harness, one task, one reporter, or incomplete coverage. -->
```

## Maintainer Validation

After the reporter posts this reply, rerun live sync or preview conversion before writing usage evidence:

```bash
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/1 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

This reply is not usage proof until it passes lint and is converted into a validated usage record.

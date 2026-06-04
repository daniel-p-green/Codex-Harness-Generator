# External Usage Pilot: LLM app pilot

GitHub issue drafts help open public pilot intake issues; they are not usage proof until a real task is completed, privacy-reviewed, and converted into a validated usage record.

## Reporter Instructions

Would you be willing to try one small real Codex task using LLM app pilot?

- Domain: LLM app
- Pilot pack: Docs/Environment/beta-exit-pilot-materials/llm-app-pilot-pilot-pack.md
- Issue draft: Docs/Environment/beta-exit-pilot-materials/llm-app-pilot-usage-issue.md

Please pick one privacy-safe task, run the generated harness checks, record the task trial,
and share either the completed issue draft or a private copied harness directory with public-safe evidence.

Do not include secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.
A private-summary report is fine if the raw evidence cannot be public.

After completing one privacy-safe task, reply to this issue with the completion template below. If the reply passes lint, maintainers can preview it with `codex-harness usage-from-github-issue https://github.com/daniel-p-green/Codex-Harness-Generator/issues/3 --include-comments --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json` before writing a usage record.
Keep evidence public-safe: no secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.

## Reporter Completion Reply Template

Copy this section into a new issue comment after the pilot task, then replace the guidance text with your public-safe result.

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

## Maintainer Preview Commands

```bash
codex-harness usage-from-issue <this-issue-body.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue <this-issue-body.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

## Usage Report Body

### Pilot or usage-record slug

llm-app-pilot

### Domain or project type

LLM app

### Generated harness profile or label

LLM App Workspace Pilot

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

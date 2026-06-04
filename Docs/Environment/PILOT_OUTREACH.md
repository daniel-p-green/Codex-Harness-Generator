# Pilot Outreach Packet

Generated: 2026-06-04T16:31:35Z
Status: PASS
Readiness: outreach-ready

Outreach packets help request and track pilots; they are not usage proof until a real task is completed and converted into a validated usage record.

## Summary

- Outreach-ready pilots: 1
- Included statuses: prepared, invited, completed
- Pilot board readiness: pilot-funnel-active

## Outreach Items

### 1. LLM app pilot (`llm-app-pilot`)

- Status: `prepared`
- Domain: LLM app
- Source type: `external`
- Generation path: `installed-quickstart`
- Pilot pack: `Docs/Environment/LLM_APP_PILOT_PACK.md`
- Issue draft: `Docs/Environment/LLM_APP_USAGE_ISSUE_DRAFT.md`

Reporter message:

```text
Would you be willing to try one small real Codex task using LLM app pilot?

- Domain: LLM app
- Pilot pack: Docs/Environment/LLM_APP_PILOT_PACK.md
- Issue draft: Docs/Environment/LLM_APP_USAGE_ISSUE_DRAFT.md

Please pick one privacy-safe task, run the generated harness checks, record the task trial,
and share either the completed issue draft or a private copied harness directory with public-safe evidence.

Do not include secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.
A private-summary report is fine if the raw evidence cannot be public.
```

Maintainer tracking:

```bash
codex-harness pilot-update llm-app-pilot --status invited --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "sent to reporter"
codex-harness pilot-update llm-app-pilot --status completed --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "reporter completed task and shared public-safe evidence"
```

Issue-body conversion:

```bash
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

Copied-harness conversion:

```bash
codex-harness usage-from-harness <generated-harness> --slug llm-app-pilot --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-harness <generated-harness> --slug llm-app-pilot --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

## Claim Boundary

Sending or tracking an invite is not adoption evidence. Count only completed, privacy-reviewed task evidence converted into valid usage records.

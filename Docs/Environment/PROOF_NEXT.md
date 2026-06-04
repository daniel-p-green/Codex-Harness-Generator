# Proof Next Actions

Generated: 2026-06-04T16:18:04Z
Status: PASS
Readiness: missing-beta-exit-evidence

This packet turns the current proof gap into the next concrete operator actions.
It is a collection plan, not evidence by itself.

## Current Gap

- Usage records to add: 3
- External or multi-project records to add: 3
- Distinct domains to add: 3
- Installed brief-based generation records to add: 2

## Suggested Pilot Coverage Projection

Projection assumes every suggested pilot is completed and converted into valid non-synthetic evidence; it is not usage proof.

- Suggested pilots in projection: 3
- Would satisfy beta-exit usage thresholds: true
- Projected usage records: 5
- Projected external or multi-project records: 3
- Projected distinct domains: 4
- Projected installed brief-based generation records: 3

Projected remaining gaps after suggested pilots:

- Usage records: 0
- External or multi-project records: 0
- Distinct domains: 0
- Installed brief-based generation records: 0

## Next Pilot

- Domain: LLM app
- Profile: `llm-app`
- Source type: `external`
- Generation path: `installed-quickstart`
- Slug: `llm-app-pilot`

## Active Pilot

- Slug: `llm-app-pilot`
- Status: `prepared`
- Pilot pack: `Docs/Environment/LLM_APP_PILOT_PACK.md`
- Issue draft: `Docs/Environment/LLM_APP_USAGE_ISSUE_DRAFT.md`

Continue this pilot instead of preparing a duplicate.

## Command Sequence

1. refresh gaps

Purpose: confirm the beta-exit usage gap before preparing more outreach

```bash
codex-harness usage-gaps --record-dir Docs/Environment/usage-records
```

2. preview pilot batch

Purpose: preview the full suggested pilot batch before deciding whether to prepare every candidate

```bash
codex-harness prepare-pilot-batch --record-dir Docs/Environment/usage-records --target-root /tmp/codex-beta-exit-pilots --pilot-record-dir Docs/Environment/pilot-records --dry-run
```

3. review active pilot

Purpose: continue the already prepared pilot instead of preparing a duplicate

```bash
codex-harness pilot-board --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md
```

4. mark pilot invited

Purpose: record outreach after the pilot pack is sent to a reporter

```bash
codex-harness pilot-update llm-app-pilot --status invited --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "sent to reporter"
```

5. mark pilot completed

Purpose: record reporter completion before converting the evidence into a usage record

```bash
codex-harness pilot-update llm-app-pilot --status completed --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "reporter completed task and shared public-safe evidence"
```

6. preview copied-harness evidence

Purpose: validate the generated harness's local eval and task-trial evidence without writing a usage record or mutating the pilot board

```bash
codex-harness usage-from-harness <generated-harness> --slug llm-app-pilot --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

7. convert copied-harness evidence

Purpose: write the checked usage record and convert the matching pilot after preview output is reviewed

```bash
codex-harness usage-from-harness <generated-harness> --slug llm-app-pilot --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

8. lint issue evidence

Purpose: show missing fields, weak evidence counts, and privacy problems before attempting conversion

```bash
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
```

9. preview issue evidence

Purpose: validate a completed reporter issue body without writing a usage record or mutating the pilot board

```bash
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

10. convert issue evidence

Purpose: write the checked usage record and convert the matching pilot after preview output is reviewed

```bash
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

11. audit beta exit

Purpose: refresh the non-gating readiness audit after each converted usage record

```bash
codex-harness beta-exit-audit --record-dir Docs/Environment/usage-records --pilot-record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records
```

12. run final proof status

Purpose: only use this as a beta-exit gate after usage thresholds are satisfied

```bash
codex-harness proof-status --beta-exit --record-dir Docs/Environment/usage-records
```

## Recommendations

- Collect 3 more external or multi-project usage record(s).
- Make at least 2 of the next record(s) use installed brief-based generation (`codex-harness prepare-next-pilot`, `codex-harness prepare-pilot`, `codex-harness quickstart`, or `codex-harness init --brief`).
- Cover 3 more distinct usage domain(s) instead of adding more same-domain proof.
- Add 3 more valid non-synthetic usage record(s).
- For the next suggested pilot, run `codex-harness prepare-next-pilot <target> --pilot-record-dir Docs/Environment/pilot-records` or copy the `codex-harness prepare-pilot <target>` command, review the generated pack, track it with `codex-harness pilot-board`, update status with `codex-harness pilot-update`, then convert completed evidence with `usage-from-harness` or `usage-from-issue`.

## Claim Boundary

This packet gives next actions for collecting evidence; it does not itself prove external adoption, beta-exit readiness, or production suitability.

This does not prove:
- A prepared pilot was completed.
- External or multi-project usage evidence exists.
- The README can drop the beta label.
- Future generated harnesses will work well for every project.

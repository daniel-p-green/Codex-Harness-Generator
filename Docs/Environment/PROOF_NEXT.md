# Proof Next Actions

Generated: 2026-06-04T14:11:03Z
Status: PASS
Readiness: missing-beta-exit-evidence

This packet turns the current proof gap into the next concrete operator actions.
It is a collection plan, not evidence by itself.

## Current Gap

- Usage records to add: 3
- External or multi-project records to add: 3
- Distinct domains to add: 3
- Installed brief-based generation records to add: 2

## Next Pilot

- Domain: LLM app
- Profile: `llm-app`
- Source type: `external`
- Generation path: `installed-quickstart`
- Slug: `llm-app-pilot`

## Command Sequence

1. refresh gaps

Purpose: confirm the beta-exit usage gap before preparing more outreach

```bash
codex-harness usage-gaps --record-dir Docs/Environment/usage-records
```

2. prepare next pilot

Purpose: generate the next recommended harness, pilot pack, issue draft, and prepared-pilot record

```bash
codex-harness prepare-next-pilot /tmp/codex-llm-app-pilot --record-dir Docs/Environment/usage-records --pilot-record-dir Docs/Environment/pilot-records --out /tmp/NEXT_EXTERNAL_PILOT_PACK.md --issue-out /tmp/NEXT_EXTERNAL_USAGE_ISSUE_DRAFT.md --force
```

3. review pilot board

Purpose: verify the prepared pilot is tracked but not counted as usage proof

```bash
codex-harness pilot-board --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md
```

4. convert completed evidence

Purpose: convert a completed reporter issue into checked usage evidence and update the pilot board

```bash
codex-harness usage-from-issue <completed-issue.md> --slug llm-app-pilot --title "LLM app pilot" --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

5. audit beta exit

Purpose: refresh the non-gating readiness audit after each converted usage record

```bash
codex-harness beta-exit-audit --record-dir Docs/Environment/usage-records --pilot-record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records
```

6. run final proof status

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

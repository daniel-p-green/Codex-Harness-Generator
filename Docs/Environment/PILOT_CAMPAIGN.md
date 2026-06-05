# External Pilot Campaign

Generated: 2026-06-05T00:14:19Z
Status: PASS
Readiness: beta-exit-evidence-ready

This campaign packet turns the current beta-exit evidence gaps into
concrete external or multi-project pilot asks. It is an evidence
collection plan, not adoption proof.
Use `codex-harness prepare-next-pilot <target> --pilot-record-dir Docs/Environment/pilot-records`
to prepare the first suggested pilot directly from the current gaps and
track it with `codex-harness pilot-board`.

## Current Evidence Gap

- Valid usage records: 8
- External or multi-project records: 3
- Distinct domains: 7
- Installed brief-based generation records: 3

## Remaining Targets

- Usage records to add: 0
- External or multi-project records to add: 0
- Distinct domains to add: 0
- Installed brief-based generation records to add: 0

## Listed Pilot Coverage Projection

Projection assumes every suggested pilot is completed and converted into valid non-synthetic evidence; it is not usage proof.

- Listed pilots in projection: 0
- Would satisfy beta-exit usage thresholds: true
- Projected usage records: 8
- Projected external or multi-project records: 3
- Projected distinct domains: 7
- Projected installed brief-based generation records: 3

Projected remaining gaps after listed pilots:

- Usage records: 0
- External or multi-project records: 0
- Distinct domains: 0
- Installed brief-based generation records: 0

## Pilot Slots

- none

## Maintainer Follow-Up

After each pilot:

1. Review the pilot pack and issue draft for privacy-sensitive text.
2. Convert acceptable evidence with `codex-harness usage-from-harness` or `codex-harness usage-from-issue`.
3. Update status with `codex-harness pilot-update`, then review `codex-harness pilot-board` so completed pilots do not stay stuck as outreach.
4. Re-run `codex-harness usage-gaps` and refresh this campaign only if gaps remain.
5. Do not drop the beta label until `codex-harness proof-status` passes with the beta-exit thresholds.

## Claim Boundary

These pilots can support narrow usage evidence. They do not prove broad external adoption, longitudinal private-repo performance, production security, compliance, or every future live `/create` run.

# Usage Evidence Gaps

Generated: 2026-06-04T11:08:10Z
Status: PASS
Readiness: missing-beta-exit-evidence

This report shows what usage evidence is still missing before the repo can
honestly stop calling itself a beta.

## Targets

- Total usage records: 5
- External or multi-project records: 3
- Distinct domains: 4
- Installed `codex-harness init --brief` records: 2

## Current Summary

- Total usage records: 2
- Non-synthetic records: 2
- Successful records: 2
- External or multi-project records: 0
- Distinct domains: 1
- Installed `init --brief` records: 0

## Remaining Gaps

- Usage records: 3
- External or multi-project records: 3
- Distinct domains: 3
- Installed `init --brief` records: 2

## Represented Domains

- Codex harness generation

## Recommended Next Moves

- Collect 3 more external or multi-project usage record(s).
- Make at least 2 of the next record(s) use the installed `codex-harness init --brief` path.
- Cover 3 more distinct usage domain(s) instead of adding more same-domain proof.
- Add 3 more valid non-synthetic usage record(s).
- For each pilot, run `codex-harness pilot-pack <generated-harness> --prefill-from-trials`, review the draft, then convert it with `usage-from-harness` or `usage-from-issue`.

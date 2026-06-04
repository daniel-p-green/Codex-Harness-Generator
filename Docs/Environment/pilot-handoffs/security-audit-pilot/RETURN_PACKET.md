# security audit pilot Return Packet

Use this after the pilot task is complete. This packet is for returning
public-safe evidence; it is not usage proof until the maintainer converts it
into a validated usage record.

## Reporter Checklist

1. In the generated harness, start with `NEXT_TASK.md` and complete one small real task.
2. Run `python scripts/check-harness.py` from the generated harness.
3. Run `python scripts/run-harness-evals.py` from the generated harness.
4. Fill every `_no response_` field in `USAGE_REPORT_DRAFT.md`.
5. Return the completed `USAGE_REPORT_DRAFT.md` to the maintainer.

## Optional Reporter Lint

If `codex-harness` is installed, run this before sending the report back:

```bash
codex-harness usage-from-issue USAGE_REPORT_DRAFT.md --lint-only --json
```

## Required Evidence Shape

- Outcome: success, partial, failed, or inconclusive.
- Public-safe task summary: what you asked Codex to do and what changed.
- Evidence: at least two public-safe bullets, with no secrets or private paths.
- Verification performed: at least two concrete checks or inspections.
- Privacy review: what you removed, sanitized, or kept private.
- Limitations: at least one honest caveat about scope or confidence.

## Maintainer Use

The maintainer should preview conversion before writing a usage record:

```bash
codex-harness usage-from-issue USAGE_REPORT_DRAFT.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

## Claim Boundary

Pilot handoff folders help send and track pilots; they are not usage proof until a real task is completed and converted into a validated usage record.

# Maintainer Commands

## Tracking

```bash
codex-harness pilot-update customer-support-pilot --status invited --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "sent to reporter"
codex-harness pilot-update customer-support-pilot --status completed --record-dir Docs/Environment/pilot-records --usage-record-dir Docs/Environment/usage-records --report Docs/Environment/PILOT_BOARD.md --notes "reporter completed task and shared public-safe evidence"
```

## Issue-Body Conversion

```bash
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-issue <completed-issue.md> --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

## Copied-Harness Conversion

```bash
codex-harness usage-from-harness <generated-harness> --slug customer-support-pilot --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
codex-harness usage-from-harness <generated-harness> --slug customer-support-pilot --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --record-dir Docs/Environment/usage-records --report Docs/Environment/USAGE_RECORDS.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --json
```

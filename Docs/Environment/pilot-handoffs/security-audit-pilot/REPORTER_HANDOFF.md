# security audit pilot Reporter Handoff

## Message

Would you be willing to try one small real Codex task using security audit pilot?

- Domain: security audit
- Pilot pack: Docs/Environment/beta-exit-pilot-materials/security-audit-pilot-pilot-pack.md
- Issue draft: Docs/Environment/beta-exit-pilot-materials/security-audit-pilot-usage-issue.md

Please pick one privacy-safe task, run the generated harness checks, record the task trial,
and share either the completed issue draft or a private copied harness directory with public-safe evidence.

Do not include secrets, personal data, proprietary source, private repository names, local machine paths, raw logs, or raw private transcripts.
A private-summary report is fine if the raw evidence cannot be public.

## Pilot Pack

# External Pilot Pack

Generated: 2026-06-04T22:31:00Z
Harness label: Security Audit Workspace Pilot
Domain: security audit
Source type: external
Generation path: installed-quickstart
Detected profile: security-audit

This pack helps a reporter try one real Codex task with a generated harness and
produce public-safe evidence. It is a pilot workflow, not a production-readiness
claim.

## Privacy Boundary

Do not share secrets, tokens, API keys, passwords, private keys, customer data,
candidate data, payment data, health data, personal data, proprietary source,
private repository names, local machine paths, email addresses, raw private logs,
or raw private transcripts.

Use `private-summary` when the raw evidence cannot be public. The public report
should describe what happened, how it was verified, the privacy review, and the
limits.

## Reporter Steps

Run these commands from the copied generated harness directory:

```bash
python scripts/check-harness.py
```

Open `NEXT_TASK.md` first. It gives the shortest reporter path for choosing a
safe task, recording evidence, running local evals, and exporting a public-safe
usage report.

Pick one small real task from `NEXT_TASK.md`, complete it with Codex,
then record the result:

```bash
python scripts/record-task-trial.py --task "short public-safe task" --outcome success --evidence "public-safe artifact or private-summary" --verification "command or reviewer check" --privacy-review "public-safe summary only" --limitations "one pilot task"
```

Then run the copied-harness eval:

```bash
python scripts/run-harness-evals.py --min-successes 1
```

## Maintainer Commands

From this generator repo, export a public-safe packet:

```bash
python scripts/codex_harness.py evidence-packet <generated-harness> --harness-label "Security Audit Workspace Pilot" --min-successes 1
```

If the packet is public-safe and complete, preview the copied-harness evidence:

```bash
python scripts/codex_harness.py usage-from-harness <generated-harness> --slug "security-audit-pilot" --evidence-type private-summary --privacy-review "Reporter confirmed public-safe private-summary evidence only." --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --no-write --json
```

After review, rerun without `--no-write` to write the usage record and convert
the matching pilot-board record.

Or convert the GitHub issue body after review:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md --lint-only --json
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md
```

## Issue Draft

- Fill out `security-audit-pilot-usage-issue.md`, then paste it into the GitHub External usage report issue.
- Keep raw evidence private unless it is already safe for public release.
- This issue draft is blank until the reporter fills it in.
- Include at least two evidence bullets, two verification bullets, one privacy
  review, and one limitation.

## Claim Discipline

One pilot is evidence for one generated harness on one task. Do not claim broad
adoption, production readiness, compliance, or long-term reliability from this
pack alone.

## Usage Issue Draft

### Pilot or usage-record slug

security-audit-pilot

### Domain or project type

security audit

### Generated harness profile or label

Security Audit Workspace Pilot

### Evidence type

private-summary

### Source type

external

### Generation path

installed-quickstart

### Outcome

_No response_

### Public-safe task summary

_No response_

### Evidence

- _No response_
- _No response_

### Verification performed

- _No response_
- _No response_

### Privacy review

Reporter confirmed the public summary excludes secrets, personal data, proprietary source, private repository names, local machine paths, email addresses, and raw private logs.

### Limitations

- One task in one generated harness; not longitudinal proof.

## Usage Report Draft

Start in the generated harness with `NEXT_TASK.md`, then complete `USAGE_REPORT_DRAFT.md` after the pilot task. The maintainer can lint it with `codex-harness usage-from-issue USAGE_REPORT_DRAFT.md --pilot-record-dir <pilot-records> --lint-only`.

## Claim Boundary

Pilot handoff folders help send and track pilots; they are not usage proof until a real task is completed and converted into a validated usage record.

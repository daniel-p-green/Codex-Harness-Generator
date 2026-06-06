# Public Pilot Recruiting

Codex Harness Generator is ready for more external usage reports. The current
repo passes its beta-exit evidence gate, but broad external adoption is still
unproven. The next useful proof is simple: one real reporter, one real
privacy-safe task, one completed usage report.

## Who To Ask

Prioritize people who can try a generated Codex harness on a real task without
sharing private source or raw logs:

- Maintainers of small public Python, JavaScript, or documentation repos.
- Builders of LLM apps, RAG workflows, or agent prototypes.
- Security, support, legal, data, hiring, or research operators who can report
  public-safe summaries.
- Codex users who already know what a good `AGENTS.md` or eval loop should do.

Avoid recruiting people who would need to expose customer data, candidate data,
secrets, private paths, proprietary code, or raw private transcripts.

## Reporter Ask

Copy this into a DM, email, Slack message, or GitHub comment:

```text
Would you be willing to try Codex Harness Generator on one real Codex task?

The ask is intentionally small:

1. Generate a harness for one privacy-safe project or task.
2. Use it for one real task.
3. Run the generated local check or eval.
4. Submit a public-safe External usage report.

Please do not share secrets, personal data, private repo names, local paths,
proprietary source, raw logs, or raw private transcripts. Summaries are fine.

Repo: https://github.com/daniel-p-green/Codex-Harness-Generator
Issue form: https://github.com/daniel-p-green/Codex-Harness-Generator/issues/new?template=external-usage-report.yml
```

## Fast Reporter Path

Reporters can use this path without reading the full maintainer packet:

```bash
pipx install git+https://github.com/daniel-p-green/Codex-Harness-Generator.git
codex-harness quickstart /tmp/codex-pilot-harness \
  --brief "Create a Codex harness for one privacy-safe task I can test today."
cd /tmp/codex-pilot-harness
python scripts/check-harness.py
python scripts/run-harness-evals.py
```

After a successful task trial, submit the public-safe issue form:

https://github.com/daniel-p-green/Codex-Harness-Generator/issues/new?template=external-usage-report.yml

## What Counts

A useful report needs all of these:

- Outcome: `success`, `partial`, `failed`, or `inconclusive`.
- Public-safe task summary.
- At least two evidence bullets.
- At least two verification bullets.
- Privacy review confirming sensitive details were removed or summarized.
- At least one limitation.

Opened issues, prepared pilots, lint comments, handoff folders, and maintainer
follow-ups do not count as adoption proof. Only converted, validated usage
records count.

## Maintainer Loop

After a reporter submits or comments:

```bash
codex-harness pilot-github-sync \
  --record-dir Docs/Environment/pilot-records \
  --usage-record-dir Docs/Environment/usage-records \
  --usage-report Docs/Environment/USAGE_RECORDS.md \
  --pilot-board-report Docs/Environment/PILOT_BOARD.md \
  --report Docs/Environment/PILOT_GITHUB_SYNC.md \
  --followup-dir Docs/Environment/pilot-github-followups \
  --repo daniel-p-green/Codex-Harness-Generator

codex-harness pilot-next-action
codex-harness beta-status
```

If an issue is conversion-ready, preview before writing:

```bash
codex-harness usage-from-github-issue <issue-number> \
  --repo daniel-p-green/Codex-Harness-Generator \
  --include-comments \
  --record-dir Docs/Environment/usage-records \
  --report Docs/Environment/USAGE_RECORDS.md \
  --pilot-record-dir Docs/Environment/pilot-records \
  --pilot-board-report Docs/Environment/PILOT_BOARD.md \
  --no-write \
  --json
```

Then run the same command without `--no-write` only if the preview is clean and
the report is public-safe.

## Claim Boundary

This recruiting note helps collect evidence. It does not prove adoption,
quality, security, compliance, or longitudinal performance by itself.

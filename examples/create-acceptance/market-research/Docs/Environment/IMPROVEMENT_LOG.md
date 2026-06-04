# Improvement Log

Use this log to turn repeated Codex friction into small, verified harness
updates. Do not rewrite the harness from a single annoyance; wait for a repeated
pattern or a clear correction from the user.

Append entries manually or with:

```bash
python scripts/record-improvement.py --category CHECK_GAP --task "short task" --friction "what went wrong" --evidence "file or command evidence"
```

Summarize the improvement backlog with:

```bash
python scripts/summarize-improvements.py
```

## Categories

| Category | Use when | Candidate update |
|---|---|---|
| CHECK_GAP | Codex could not find a runnable check or used the wrong one. | Update `Docs/Environment/EVAL_PLAN.md` or `AGENTS.md` verification rules. |
| ROUTING_CORRECTION | The user corrected which files, workflow, or reviewer path mattered. | Update `AGENTS.md`, `.codex/rules/core.md`, or reviewer focus. |
| PERMISSION_FRICTION | A needed safe command, path, or domain was blocked. | Update `.codex/config.toml` only after confirming scope and risk. |
| SOURCE_FIDELITY | Codex summarized, edited, or claimed beyond available source evidence. | Add stronger source-check language to `AGENTS.md` or the eval plan. |
| DOMAIN_RISK | A market research risk was missed or under-explained. | Add a domain guardrail, reviewer instruction, or acceptance check. |

## Seed Patterns

- [PATTERN] Missing project command: if two tasks lack a clear runnable check,
  add the real command to `Docs/Environment/EVAL_PLAN.md`.
- [PATTERN] Reviewer too late: if review happens after final reporting, update
  `AGENTS.md` or `.codex/rules/core.md` to route non-trivial work to reviewer
  before final response.
- [PATTERN] Permission mismatch: if the same safe local path or command is
  blocked twice, document the scope here before changing `.codex/config.toml`.

## Entry Template

```text
Date:
Category:
Task:
Observed friction:
Evidence:
User correction, if any:
Candidate harness update:
Verification after update:
Status: open | proposed | applied | rejected
```

## Update Rule

Only apply a harness update when the entry has evidence and the proposed change
directly addresses the friction. After an update, run:

```bash
python scripts/check-harness.py
python scripts/summarize-improvements.py
```

Then run the relevant check from `Docs/Environment/EVAL_PLAN.md`.

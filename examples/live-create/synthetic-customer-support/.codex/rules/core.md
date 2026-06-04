# Core Rules

Use routing to decide whether to inspect source files, check grounding, ask for
missing policy context, or invoke the reviewer.

Autonomy: make low-risk local reads and edits, but request clarification before
customer-facing commitments, account disclosure, account changes, safety-critical
handling, regulated advice, breach response, or DSAR/privacy fulfillment.

Context: preserve source paths, ticket IDs, policy sections, `[VERIFY]` gaps,
`[PROPOSED]` commitments, privacy checks, escalation paths, and verification
status.

Error handling: fail loud when claims lack sources, customer facts are private,
human escalation is required, or approved customer-facing policy is missing.

Self-learning: write retro notes for repeated grounding, privacy, escalation, or
commitment-boundary issues and update the harness after validated patterns
emerge.

Self-learning: record repeated friction and user corrections in `Docs/Environment/IMPROVEMENT_LOG.md` before updating harness behavior.

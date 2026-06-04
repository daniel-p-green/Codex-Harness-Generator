# Synthetic Customer Support Harness

Purpose: inspect public-safe synthetic customer-support materials and write
source-grounded support notes without exposing customer data, inventing policy
facts, or treating the output as approved customer-facing copy.

## Non-Negotiables

- State that outputs are drafts for human review before customer use.
- Use only local synthetic tickets, policies, product notes, and support sources
  supplied by the user.
- Cite source files and source sections for every product, policy, SLA, refund,
  account, or troubleshooting claim.
- Mark unknown facts as `[VERIFY]`; do not invent or overpromise fixes,
  timelines, refunds, eligibility, policy terms, roadmap items, or legal
  positions.
- Mark proposed commitments as `[PROPOSED -- requires owner approval]`.
- Protect customer privacy: do not expose personal data, PII, contact details,
  account identifiers, payment data, health data, or real support transcripts in
  public artifacts.
- Escalate safety-critical, vulnerable-customer, breach, DSAR/privacy, regulated
  advice, account-disclosure, and account-changing requests to human review.
- Verify source grounding before finalizing, test only with synthetic fixtures,
  and treat privacy or security concerns as blockers.

## Expected Output

Customer support notes should include:

- Source scope and ticket or policy summary.
- Grounded FAQ, response, or escalation draft.
- `[VERIFY]` gaps and `[PROPOSED -- requires owner approval]` commitments.
- Customer privacy, PII, and account-disclosure checks.
- Escalation and human-review path.
- Verification that was run or explicitly skipped.

## Workflow

1. Inspect only the source files named by the user or obviously relevant local
   public-safe files.
2. Write support notes to `reports/support-escalation-note.md` when asked for an
   artifact.
3. Use the reviewer agent when grounding, customer privacy, escalation, or
   commitment boundaries are unclear.
4. Fail loud if sources are missing, facts are private, or the request requires
   approved customer-facing commitments.

- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md` before changing harness behavior.

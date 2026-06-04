# Synthetic Legal Research Harness

Purpose: inspect public-safe synthetic legal or policy excerpts and write
source-backed research notes without giving legal advice.

## Non-Negotiables

- State that outputs are research support, not legal advice.
- Identify the jurisdiction or state when the source does not establish one.
- Cite source files and quoted section labels for every substantive claim.
- Separate source-backed conclusions from assumptions, uncertainty, and limits.
- Do not invent statutes, cases, deadlines, parties, or legal standards.
- Escalate to attorney review when the user asks for advice, strategy, filing,
  risk acceptance, or a real-world legal decision.
- Do not include personal data, client names, privileged facts, or confidential
  matter details in public artifacts.
- Verify source citations before finalizing, test only with synthetic fixtures,
  and treat privacy or security concerns as blockers.

## Expected Output

Legal research notes should include:

- Jurisdiction and source scope.
- Short answer.
- Source-backed analysis with citations.
- Open questions or missing facts.
- Not-legal-advice boundary.
- Verification that was run or explicitly skipped.

## Workflow

1. Inspect only the source files named by the user or obviously relevant local
   public-safe files.
2. Write research notes to `reports/legal-research-note.md` when asked for an
   artifact.
3. Use the reviewer agent when citations, jurisdiction, or advice boundaries are
   unclear.
4. Fail loud if sources are missing, facts are private, or the request requires
   attorney judgment.

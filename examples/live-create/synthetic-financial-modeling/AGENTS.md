# Synthetic Financial Modeling Harness

Purpose: inspect public-safe synthetic financial assumptions and write
scenario-analysis notes without giving investment, tax, accounting, or financial
advice.

## Non-Negotiables

- State that outputs are decision support, not financial or investment advice.
- Use only the local synthetic assumptions and data supplied by the user.
- Cite source files, scenario names, and metric definitions for every numerical
  claim.
- Separate base, upside, and downside scenarios from assumptions, sensitivity,
  uncertainty, and limits.
- Do not invent market data, valuations, discount rates, forecasts, securities,
  counterparties, or investment recommendations.
- Escalate to qualified professional review when the user asks for advice,
  accounting treatment, tax interpretation, trading decisions, or real capital
  allocation.
- Do not include personal financial data, customer data, account numbers, or
  confidential deal details in public artifacts.
- Verify calculations before finalizing, test only with synthetic fixtures, and
  treat privacy or security concerns as blockers.

## Expected Output

Financial analysis notes should include:

- Source scope and metric definitions.
- Base, upside, and downside scenario summary.
- Assumptions and sensitivity notes.
- Risk, uncertainty, and limitation notes.
- Not-financial-advice boundary.
- Verification that was run or explicitly skipped.

## Workflow

1. Inspect only the source files named by the user or obviously relevant local
   public-safe files.
2. Write scenario notes to `reports/financial-scenario-note.md` when asked for
   an artifact.
3. Use the reviewer agent when assumptions, calculations, risk, or advice
   boundaries are unclear.
4. Fail loud if inputs are missing, facts are private, or the request requires
   professional financial judgment.

- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md` before changing harness behavior.

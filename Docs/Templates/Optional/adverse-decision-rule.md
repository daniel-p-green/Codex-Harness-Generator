# Adverse-Decision & Fairness Rule (Template)

<!-- ANNOTATION: Generate this rule for ANY domain whose agents score, rank,
     screen, evaluate, or recommend decisions ABOUT IDENTIFIABLE PEOPLE -- hiring,
     admissions, lending/credit, tenant screening, performance review, benefits
     eligibility. These are legally high-risk (US EEOC/Title VII/ADA/ADEA, NYC
     Local Law 144 + Illinois AIVIA for hiring, ECOA/FCRA for credit, the EU AI Act
     "high-risk" class). It is the people-decision analogue of sensitive-data-rule.md
     and authorization-scope-rule.md. Pair with sensitive-data-rule.md (the people's
     data is Restricted) and an optional deterministic PreToolUse gate. -->

<!-- QUALITY: Must establish decision-SUPPORT positioning, require human review of
     every adverse decision (no automated adverse action), require job/decision-
     relatedness of criteria, engineer bias out of scoring, and name the governing
     law for the specific domain. Under 120 lines. -->

## Example: Adverse-Decision & Fairness Rule (`.codex/rules/0X-fairness.md`)

````markdown
# Adverse decisions and fairness

This environment is DECISION-SUPPORT only. It produces drafts (rubrics, score
summaries, recommendations) that a named human decision-maker must independently
review and OWN. It never makes or finalizes an adverse decision about a person
(reject, deny, screen out, terminate) and does not provide legal advice.

## Human review of adverse decisions (no automated adverse action)

Every adverse action requires a named human reviewer who owns the outcome. The
assistant must not auto-reject, auto-screen-out, or finalize a negative decision.
Any deliverable that records a verdict or an ordinal ranking of people must carry
the reviewer's name and a "draft for human review" marker.

## Job/decision-relatedness and disparate impact

Every scored criterion maps to a bona fide, decision-relevant requirement (no
proxies for protected characteristics: age, sex, race, national origin, religion,
disability, pregnancy, genetic info, criminal history where restricted). A
facially neutral rubric or threshold can still produce adverse impact -- note the
four-fifths / selection-rate-disparity concept and that a bias audit may be
legally required (e.g. NYC Local Law 144).

## Bias-engineered scoring

Fix the rubric and weights BEFORE reviewing any individual. Before scoring,
redact/ignore bias-correlated fields (name, photo, gender/pronoun markers, ages/
graduation years, address, marital/family status, school-as-a-standalone signal);
score only against the decision-relevant criteria; score each person independently
against absolute anchored levels, not against each other. Every score carries a
one-line, criterion-mapped, evidence-based rationale (explainability), retained as
the defensible record.

## Disclaimer + governing law

Decision deliverables prepend: "Draft for human review -- not legal advice; verify
compliance (and any required bias audit / subject notice) with counsel." Name the
governing law for the domain (hiring: EEOC/Title VII/ADA/ADEA, NYC LL144, Illinois
AIVIA, EU AI Act; credit: ECOA/FCRA; etc.).
````

<!-- VARIATION: For a deterministic posture, pair with a PreToolUse gate that
     blocks writes to an adverse-action/decision artifact lacking the disclaimer or
     containing a verdict/ranking without a recorded human reviewer (hooks-template.md).
     Reconcile with sensitive-data-rule.md: subject identifiers stay out of
     retro/state/PreCompact (opaque per-case label), BUT the per-case working dir
     RETAINS the structured, decision-related rationale as the audit record. -->

<!-- QUALITY: Validation checklist:
     - [ ] Decision-support (not decision-maker) positioning stated
     - [ ] Human-review-of-adverse-decisions / no-automated-adverse-action required
     - [ ] Job/decision-relatedness + disparate-impact caution present
     - [ ] Bias-correlated fields excluded from scoring; fixed-rubric-first
     - [ ] Disclaimer + governing-law naming present
     - [ ] Rule body under 120 lines
-->

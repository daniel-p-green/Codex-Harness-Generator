# Template: Sensitive Data Rule (07-sensitive-data.md)

<!-- TEMPLATE ANNOTATION
  This template defines handling rules for regulated and sensitive data. It is
  used by the architect's Pattern A when the domain involves PII, PHI, financial
  records, student records, or other data subject to regulatory requirements.
  It complements 06-data-handling.md (which covers general data safety) with
  classification-specific handling and audit requirements.

  QUALITY CRITERIA:
  - Under 130 lines in generated output
  - Data classification categories with clear definitions
  - Handling rules per category (logging, output, redaction)
  - PII/PHI detection patterns enumerated
  - Regulatory considerations (HIPAA/FERPA/GDPR as applicable)
  - Audit trail requirements
  - Unexpected sensitive data protocol
  - Integration with data-handling rule

  WHY THIS EXISTS:
  Even in a local Codex environment, sensitive data can leak into session
  logs, memory files, retro entries, and context summaries. A data analyst
  processing healthcare claims or student records needs clear guardrails to
  prevent accidental exposure. This rule provides classification-based handling
  that scales from "be careful" to "strict compliance."
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: Healthcare data analytics (HIPAA-adjacent)
============================================================ -->

# Sensitive data handling

<!-- CORE PRINCIPLE
  WHY: Classification-first approach means agents do not need to make judgment
  calls about every field. Classify once, handle consistently everywhere.
-->
Data is classified before processing. Classification determines what can be
logged, output, and stored in memory.

## Classification categories

<!-- CLASSIFICATION
  WHY: Four levels provide enough granularity without over-complicating.
  Most projects only use 2-3 levels. The generator should include only
  the levels relevant to the user's domain.
-->

| Category | Definition | Examples |
|---|---|---|
| Public | Information that is or could be freely available | Company name, published financials, public records |
| Internal | Business information not meant for public release | Internal reports, draft analyses, budget forecasts |
| Confidential | Sensitive business or personal information | Employee records, client lists, unpublished financials, trade secrets |
| Restricted | Regulated data subject to legal requirements | PHI (HIPAA), student records (FERPA), EU personal data (GDPR), SSNs, financial account numbers |

When classification is unclear, treat as Confidential until confirmed otherwise.

## Handling rules per category

<!-- HANDLING RULES
  WHY: Each category has specific, actionable constraints. Agents can
  check this table instead of reasoning about sensitivity ad hoc.
-->

| Action | Public | Internal | Confidential | Restricted |
|---|---|---|---|---|
| Include in context summaries | Yes | Yes | Aggregates only | Never |
| Include in session notes (Docs/_working/sessions/) | Yes | Yes | Reference only, no values | Reference only, no values |
| Include in retro/friction logs | Yes | Yes | No | No |
| Include in report output | Yes | Yes | With access controls noted | Only with explicit user approval |
| Log sample values during validation | Yes | Yes | First 2 chars + mask | Never (count and type only) |
| Store in memory (Docs/Areas/) | Yes | Yes | Metadata only (field names, not values) | Never |

"Reference only" means you may note that the field exists and its type, but
not include actual values. Example: "Column SSN contains 9-digit identifiers
(1,247 non-null values)" -- not "SSN values include 123-45-6789."

## PII/PHI detection patterns

<!-- DETECTION PATTERNS
  WHY: Agents cannot classify data they do not recognize as sensitive.
  These patterns trigger awareness. Detection does not need to be perfect --
  false positives are acceptable, false negatives are dangerous.
-->
Flag fields that match these patterns during data validation:

**Personally Identifiable Information (PII)**:
- Names: columns named name, first_name, last_name, full_name, patient, client
- Contact: email, phone, address, city+state+zip combinations
- Identifiers: ssn, social_security, tax_id, ein, driver_license, passport
- Financial: account_number, routing_number, credit_card, card_number
- Dates combined with names: date_of_birth, dob + any name field

**Protected Health Information (PHI)**:
- Medical: diagnosis, icd_code, procedure, prescription, medication, condition
- Provider: doctor, physician, provider_name, npi, facility
- Insurance: policy_number, member_id, claim_number, group_number
- Any medical data linked to an identifiable individual

**Other regulated data**:
- Student records: student_id, gpa, grades, enrollment (FERPA)
- Children's data: age < 13 indicators, parental consent fields (COPPA)
- Biometric: fingerprint, face_encoding, iris, voice_print

When detected, report: "Sensitive data detected: [category] in columns [list].
Applying [category] handling rules."

## Regulatory considerations

<!-- REGULATORY
  WHY: The generator should include only the regulations relevant to the user's
  domain. These are reference notes, not legal advice. The rule file should
  explicitly state it is not legal compliance guidance.
-->

**Important**: This rule provides data handling best practices, not legal
compliance certification. Consult qualified legal/compliance professionals
for regulatory obligations.

Domain-specific considerations:
- **HIPAA** (healthcare): PHI must not appear in session logs or memory files.
  De-identification requires removing 18 identifier types. Minimum necessary
  principle: access only the PHI needed for the specific analysis.
- **FERPA** (education): Student records require directory information
  designation. Do not include grades, disciplinary records, or disability
  information in any output without explicit authorization.
- **GDPR** (EU personal data): Lawful basis required for processing. Data
  minimization principle applies. Right to erasure may affect retention.
- **SOX** (financial): Audit trail integrity matters. Do not modify or delete
  intermediate processing files that document financial calculations.

## Audit trail requirements

<!-- AUDIT TRAIL
  WHY: When working with sensitive data, the ability to answer "what happened
  to this data?" is essential. The audit trail tracks data access and
  transformations without recording the sensitive values themselves.
-->
For Confidential and Restricted data, maintain an audit trail in the session
notes:

```
## Data Access Log
- 2026-02-15 10:30 | Read | Inbox/patient_claims.csv | 12,847 rows | PHI detected: columns [patient_name, dob, diagnosis, ssn]
- 2026-02-15 10:32 | Transform | Filtered to Q4 2025, aggregated by diagnosis | 847 -> 42 rows (aggregated)
- 2026-02-15 10:35 | Output | output/2026-02-15_q4_claims_summary.csv | 42 rows | PHI removed (aggregates only)
```

Log: timestamp, action (Read/Transform/Output), file, row counts, sensitive
fields present. Do NOT log actual sensitive values in the audit trail.

## Unexpected sensitive data protocol

<!-- UNEXPECTED DETECTION
  WHY: Users may not realize their data contains sensitive fields. The first
  time sensitive data is detected, the environment must alert the user and
  get confirmation before proceeding.
-->
When sensitive data is detected in a file not previously flagged:

1. **Stop processing** (do not read further into the file)
2. **Alert the user**: "Sensitive data detected in [file]: [category] fields
   [column names]. How would you like to proceed?"
3. **Offer options**:
   - Continue with [category] handling rules applied
   - Exclude sensitive columns from processing
   - Stop and let user pre-process the file
4. **Record the decision** in session notes for the audit trail
5. **Proceed only after user confirms**

This is one of the few cases where the environment asks before acting,
overriding the normal autonomy rules.

## Integration with data handling

<!-- INTEGRATION
  WHY: This rule complements 06-data-handling.md. Both must be consulted
  for data processing tasks. This section clarifies the relationship.
-->
This rule works alongside `06-data-handling.md`:
- Data handling provides general safety (immutable sources, lineage, validation)
- Sensitive data adds classification-based restrictions on top
- When both rules apply, the stricter rule wins
- Validation (from data handling) triggers sensitive field detection (from this rule)

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  HEALTHCARE (this example):
  - Full PHI detection patterns
  - HIPAA considerations prominent
  - Strict audit trail requirements
  - De-identification guidance

  FINANCIAL SERVICES:
  - Focus on PII (SSN, account numbers) and financial data
  - SOX audit trail requirements
  - Regulatory: SEC, FINRA, SOX
  - Retention requirements for financial calculations

  LEGAL:
  - Attorney-client privilege considerations
  - Confidential: case details, client communications
  - Restricted: sealed records, juvenile records
  - Regulatory: varies by jurisdiction

  EDUCATION:
  - FERPA focus (student records)
  - COPPA if working with data from minors
  - Restricted: grades, disciplinary records, disability accommodations
  - Directory information exceptions

  GENERAL BUSINESS:
  - Lighter classification (Internal/Confidential only)
  - PII detection for employee and customer records
  - No specific regulatory framework (general privacy best practices)
  - May omit Restricted category entirely
-->

<!-- HOOK ENFORCEMENT BRIDGE

  This rule is ADVISORY -- it depends on the model following instructions.
  For regulated industries (HIPAA, SOX, GDPR, PCI-DSS), pair this rule with
  deterministic hook enforcement from hooks-template.md:

  1. PreToolUse PII content gate: Blocks writes containing sensitive patterns
     before the file is modified. Uses regex patterns from pii-patterns.conf.
     This is the primary enforcement mechanism.

  2. UserPromptSubmit input screening: Blocks accidental pasting of sensitive
     data (SSNs, credit cards) into prompts before the model sees it.

  3. PostToolUse audit trail: Records every file operation for compliance
     review. Required for SOX, recommended for all regulated environments.

  The component-generator should check GENESIS.md for sensitive data flags.
  When found:
  - Always generate this advisory rule (tells the model what to do)
  - Always generate PreToolUse PII content gate hook (enforces deterministically)
  - Always generate pii-patterns.conf with domain-appropriate patterns
  - Generate UserPromptSubmit screening if the user handles raw sensitive data
  - Generate PostToolUse audit if regulatory compliance requires action logging
  - Document hook setup in GETTING_STARTED.md

  Defense-in-depth: Advisory rule catches nuanced cases the regex misses
  (e.g., "John Smith's diagnosis"). Hooks catch literal patterns the model
  might miss under context pressure (e.g., SSN in a data dump). Together they
  provide stronger protection than either alone.
-->

<!-- ANTI-PATTERNS

  1. NO CLASSIFICATION SYSTEM
     Problem: Every field treated the same. Sensitive data leaks into logs.
     Fix: Classify first, handle per category.

  2. OVER-CLASSIFICATION
     Problem: Everything marked Restricted. Work grinds to a halt.
     Fix: Four clear levels with specific definitions and examples.

  3. LOGGING SENSITIVE VALUES
     Problem: Session notes contain SSNs, patient names, account numbers.
     Fix: Handling rules table explicitly states what can appear where.

  4. SILENT PROCESSING OF SENSITIVE DATA
     Problem: Agent processes PHI without telling the user.
     Fix: Unexpected sensitive data protocol stops and asks.

  5. COMPLIANCE CLAIMS
     Problem: Rule says "HIPAA compliant" -- it is not and cannot be.
     Fix: Explicit disclaimer: "not legal compliance certification."

  6. NO AUDIT TRAIL
     Problem: Cannot answer "what happened to this data?"
     Fix: Structured data access log in session notes.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 130 lines in generated output
  [ ] Four classification categories with definitions and examples
  [ ] Handling rules table covering: summaries, session notes, retro, reports, validation, memory
  [ ] PII detection patterns (5+ field name patterns)
  [ ] PHI detection patterns (if healthcare domain)
  [ ] At least one regulatory framework mentioned with domain-specific guidance
  [ ] Explicit "not legal compliance" disclaimer
  [ ] Audit trail format with example
  [ ] Unexpected sensitive data protocol (stop, alert, offer options, record)
  [ ] Integration note with data-handling rule
  [ ] Stricter-rule-wins principle stated
  [ ] ASCII-only
-->

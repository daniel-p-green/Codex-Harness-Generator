# Output Styles Configuration (Template)

<!-- ANNOTATION: Generate output style guidance when the user has specific
     communication preferences identified during intake. Common for
     knowledge work (executive summaries), consulting (structured reports),
     and technical leadership (data-first analysis). Output style can be
     set via settings.json "outputStyle" or via CLAUDE.md instructions. -->

<!-- QUALITY: Must include at least 2 style definitions. Must show how
     to configure via settings.json. Must include anti-Markdown option.
     Under 120 lines. -->

## How Output Styles Work

Claude Code supports an `outputStyle` setting in settings.json that provides
high-level guidance. For more specific control, include style instructions
directly in CLAUDE.md or a rule file.

```json
{
  "outputStyle": "Concise and technical. Lead with data. Use tables for comparisons."
}
```

<!-- ANNOTATION: The outputStyle setting is a free-text string. It is
     loaded into Claude's system prompt. Keep it short (1-2 sentences)
     because it applies to every response. -->

## Style Definitions

### Executive Style

<!-- VARIATION: Common for knowledge work, consulting, business analysis.
     Users who read many reports and need quick answers. -->

For CLAUDE.md or a rule file:
```markdown
## Communication style

Lead with the decision or recommendation. Follow with supporting evidence.
Structure responses for a 30-second read:

1. **Answer first**: State the conclusion or recommendation in the first sentence
2. **Key numbers**: Include relevant metrics or quantities
3. **Evidence**: Brief supporting points (3-5 bullets max)
4. **Next steps**: What action follows

Keep responses under 200 words unless asked for detail.
Use tables for comparisons. Use bullet points, not paragraphs.
```

For settings.json:
```json
{
  "outputStyle": "Executive style. Lead with the answer. Brief supporting evidence. Under 200 words. Tables for comparisons."
}
```

### Technical Style

<!-- VARIATION: Common for engineering teams, data science, research.
     Users who need to verify methodology and reproduce results. -->

For CLAUDE.md or a rule file:
```markdown
## Communication style

Lead with data and methodology. Include enough detail for reproduction.

1. **Context**: What was analyzed and why
2. **Methodology**: How the analysis was done (commands run, files read)
3. **Findings**: Data-first, with specific values and file paths
4. **Interpretation**: What the findings mean
5. **Confidence**: How certain the conclusion is and what could change it

Include exact file paths, line numbers, and command output.
Prefer precision over brevity.
```

For settings.json:
```json
{
  "outputStyle": "Technical style. Data-first. Include file paths and line numbers. Methodology before conclusions."
}
```

### Creative Style

<!-- VARIATION: Common for content creation, marketing, writing projects.
     Users who want natural-sounding prose, not structured reports. -->

For CLAUDE.md or a rule file:
```markdown
## Communication style

Write in natural prose. Avoid bullet-point lists and markdown headers
in conversational responses. Use formatting only for structured
deliverables (outlines, drafts, code).

Vary sentence length. Use active voice. Be direct but not robotic.
Match the tone of the project (formal for academic, casual for blog posts).
```

### Anti-Markdown (Prose Mode)

<!-- ANNOTATION: Some users find Claude's default heavy use of markdown
     headers, bullet points, and bold text distracting. This prompt
     suppresses that behavior for conversational responses while
     preserving formatting for actual deliverables. -->

For CLAUDE.md:
```markdown
## Communication style

Do not use markdown formatting (headers, bullet lists, bold, code blocks)
in conversational responses. Write in plain prose paragraphs.

Use markdown formatting ONLY when:
- Producing a deliverable document (report, specification, code)
- Showing code snippets
- Presenting tabular data

In conversation, write naturally. A short paragraph is better than a
bulleted list.
```

For settings.json:
```json
{
  "outputStyle": "Plain prose in conversation. No markdown formatting except for deliverables and code. Short paragraphs."
}
```

### Client Proposal / Deliverable Format

<!-- VARIATION: Common for consulting, professional services, legal, agencies.
     Users who need to produce client-facing documents with clear deliverables. -->

For CLAUDE.md or a rule file:
```markdown
## Communication style: Client deliverable

Characteristics:
- Professional tone, addressed to the client by name/organization
- Lead with the value proposition or recommendation
- Scope of work with clear deliverables and timelines
- Pricing or effort estimate (if applicable)
- Next steps with specific action items
- Appendix for methodology or supporting detail
- Branding-neutral (the user adds their own branding)
```

### Regulatory / Compliance Format

<!-- VARIATION: Common for cybersecurity, financial services, healthcare,
     legal compliance. Users who produce audit reports or gap analyses. -->

For CLAUDE.md or a rule file:
```markdown
## Communication style: Regulatory compliance

Characteristics:
- Reference specific regulation sections (e.g., "Per 23 NYCRR 500.02(a)")
- Structured by regulatory requirement, not by topic
- Gap analysis format: Requirement | Current State | Gap | Remediation
- Evidence-based: cite specific policies, procedures, or controls
- Risk ratings per finding (Critical / High / Medium / Low)
- Compliance status summary (Compliant / Partially Compliant / Non-Compliant)
- Action items with owners, deadlines, and regulatory deadlines
```

### Financial / Tabular Format

<!-- VARIATION: Common for finance, accounting, FP&A, business analysis.
     Users who work with financial statements, budgets, and forecasts. -->

For CLAUDE.md or a rule file:
```markdown
## Communication style: Financial tabular

Characteristics:
- Standard accounting layout where applicable (Revenue -> COGS -> Gross Profit -> OpEx -> EBITDA -> Net Income)
- Right-aligned numbers with consistent decimal places (2 for currency, 1 for percentages)
- Parentheses for negative numbers, not minus signs
- Thousands separator for numbers >= 1,000
- Clear column headers with units and periods (Q1 2026, FY2025, etc.)
- Subtotals and totals on separate clearly-marked rows
- Variance columns showing both absolute and percentage change
- Footnotes for assumptions, adjustments, and data sources
- Source data attribution at bottom of each table
```

## Combining Styles with Domain Context

<!-- ANNOTATION: The most effective output style combines a communication
     preference with domain-specific vocabulary guidance. -->

```markdown
## Communication style

Use executive style: lead with the answer, support with evidence, under
200 words. Use the team's vocabulary:
- "endpoint" not "route" or "API path"
- "deployment" not "release" or "push"
- "incident" not "bug" or "issue" (for production problems)
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] At least one style defined (matched to intake preferences)
     - [ ] Settings.json outputStyle shown if applicable
     - [ ] Style instructions are actionable (not vague)
     - [ ] Anti-Markdown option available for non-technical users
     - [ ] Domain vocabulary included if identified in intake
     - [ ] Under 120 lines total for generated rule
-->

<!-- ANTI-PATTERN: Do not include all four styles in a generated environment.
     Pick the ONE style that matches the user's preferences. Including
     multiple styles creates confusion about which to follow. -->

<!-- ANTI-PATTERN: Do not set outputStyle to extremely long text. It is
     loaded on every request. Keep it under 100 characters. Use a rule
     file for detailed style guidance. -->

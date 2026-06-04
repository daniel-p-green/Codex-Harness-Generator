# Starter Profile: Knowledge Work

Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim). A starting point the
architect adapts -- it points at templates, it does not inline them.

## Profile Metadata

- **Target audience**: researchers, lawyers, financial analysts, technical
  writers, policy analysts, consultants, grant writers -- professionals whose
  primary output is documents and analysis
- **Domains**: legal, academic research, financial analysis, technical writing,
  policy analysis, strategy consulting, grant writing, compliance
- **Complexity**: Lite | **Memory tier**: Lite (solo) or Standard (team of 2-5) |
  **Action default**: conservative (ask before external actions; confirm before
  overwriting existing documents) | **VCS**: None (document-centric workflow)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| researcher | high-effort | Find and synthesize info; primary sources, cited claims, confidence levels (read-only) | researcher.md |
| drafter | medium-effort | Write/edit memos, reports, analyses in the chosen output style | drafter.md |
| reviewer | high-effort | Check accuracy, completeness, citations, compliance; classify findings (read-only) | reviewer.md |
| analyst | high-effort | (conditional) Read brand assets / data, refresh brand-rules.md (read-only) | analyst.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing
(conservative default, human-review gate for external-audience docs,
research-before-write gap analysis), autonomy, context-management (preserve
research sources + citations + draft status), self-learning, error-handling
(unavailable/paywalled sources, ambiguous requests), memory-management.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`
(no VCS category), `/state-load`, `/update`, `/health-check`; domain
`/process-inbox` (Inbox/ -> MarkItDown -> process -> Outbox/).

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Research a topic / find information | researcher | Specify scope, time range, source preferences | answer directly (simple factual question) |
| 2 | Draft a memo / report / document | drafter | Include audience, purpose, length, style | researcher first (topic unfamiliar) |
| 3 | Review / proofread a document | reviewer | Provide document path and review criteria | answer directly (single paragraph) |
| 4 | Compare approaches / options analysis | researcher -> drafter (comparison table) | Define comparison criteria explicitly | answer directly (2-option comparison) |
| 5 | Fact-check claims / verify accuracy | reviewer -> researcher (disputed facts) | Provide document or claims to check | answer directly (single verifiable fact) |
| 6 | Compliance / regulatory check | reviewer (vs requirements) -> researcher (current regs) | Specify jurisdiction and applicable regulations | answer directly (well-known requirement) |
| 7 | Summarize a long document | answer directly (read and summarize) | Specify desired length and focus areas | researcher (multiple docs to synthesize) |
| 8 | "Improve this writing" / style edit | drafter (revise with style guidance) | Specify target audience and tone | reviewer first (unsure what needs improving) |
| 9 | Citation / reference management | researcher (find and format citations) | Specify style (APA, Bluebook, Chicago) | answer directly (reformat existing citations) |
| 10 | Template / format creation | drafter (reusable template) | Based on examples or specs provided | answer directly (simple formatting question) |
| 11 | Literature review / systematic search | researcher (structured multi-source) | Define inclusion/exclusion criteria, date range | drafter (synthesize into narrative) |
| 12 | Executive summary / brief | drafter (condense existing material) | Specify audience and page/word limit | answer directly (source material short) |
| 13 | Data interpretation / analysis narrative | researcher (check methodology) -> drafter (write analysis) | Provide data source and framework | answer directly (straightforward description) |
| 14 | "Explain this concept" / knowledge question | answer directly (clear explanation) | Adapt vocabulary to user's level | researcher (needs current information) |
| 15 | Contract / agreement review | reviewer (check terms, flag risks) | Specify jurisdiction and party interests | researcher (unfamiliar clause type) |
| 16 | Meeting notes / action items | answer directly (structure and extract) | Provide raw notes or transcript | drafter (formal minutes required) |
| 17 | Formatted output (.docx/.pdf) | drafter (Markdown) -> Pandoc converts | Pandoc required; falls back to Markdown if absent | drafter (Markdown-only) |
| 18 | Review a document from Inbox/ | MarkItDown -> reviewer (analyze content) | Supports Word, PDF, Excel, PowerPoint inbound | answer directly (already plain text) |
| 19 | Process the file(s) in Inbox/ | /process-inbox: MarkItDown -> process -> Outbox/ | Batch-processes multiple files | answer directly (single simple file) |
| 20 | Update brand rules / re-read brand guide | analyst reads Brand/ via MarkItDown, updates brand-rules.md | Re-analyzes Brand/Guidelines/ + Brand/Templates/ | answer directly (no Brand/ dir) |

Complexity scaling: Simple (direct answer, <3 tool calls: factual questions,
formatting, short summaries) | Standard (1-2 agents, 5-10 calls each: research,
drafting, reviews) | Complex (2-3 agents serial: literature reviews, compliance
audits, multi-source analyses).

## Ecosystem Permissions

Base + Universal Deny -- see `Docs/Templates/References/ecosystem-permissions.md`.
NO language ecosystems: this is document-centric, so deny programming tools
(`pip`, `npm`, `node`, `python`) and all VCS commands. Domain-specific additions
not in the reference:

- allow writable `Outbox/**`; safe text utilities
  `wc`, `sort`, `diff`, `date`, `head`, and `tail`; `pandoc` when installed
  for outbound .docx/.pdf.
- File conversion: prefer the MarkItDown MCP server (`npx -y
  @openai/markitdown-mcp`) over a Python dependency. If Python is unavoidable,
  document `markitdown` setup narrowly.
- Data extension (only if intake flags CSV/JSON/structured files): add
  ad hoc Python snippets, `csvtool`, and `jq`.

Generate `local config profile` for machine-specific tool paths (Pandoc/MarkItDown
install dirs).

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Too much jargon -- responses use technical AI/LLM terms
  unfamiliar to non-technical users. Mitigation: plain language in user-facing
  output; technical vocabulary only in generated files.
- [PATTERN] (pre-seeded) Research lacks citations -- researcher returns findings
  without clear attribution. Mitigation: require author, title, date, and URL for
  every factual claim.
- [PATTERN] (pre-seeded) Context lost across long research sessions -- research
  direction and source-evaluation criteria vanish after save/load. Mitigation:
  state-save captures "research strategy" and "source quality notes" as decision
  state.
- [PATTERN] (pre-seeded) Format mismatch -- output ignores the client/house style
  guide (heading levels, citation format, page limits). Mitigation: load the
  active output style before drafting; flag deviations.
- [PATTERN] (pre-seeded) Tone drift -- a single document mixes executive and
  technical register. Mitigation: pin one output style per document; reviewer
  flags register changes mid-document.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended for long research/drafting sessions) --
  appends current document, research direction, and source criteria to
  `Docs/_working/state/SESSION_CONTEXT.md`. See
  `Docs/Templates/Optional/hooks-template.md`.

## Cost / Model Notes

high-effort GPT-5.5 for researcher/reviewer (deep reasoning, cross-model accuracy checks);
medium-effort GPT-5.5 for drafter (established-pattern writing); analyst on GPT-5.5 when included.
Defaults: balanced (GPT-5.5 on research/review, medium-effort GPT-5.5 on drafting; compaction 95%;
AGENTS.md ~200 lines). Cost-conscious override: all medium-effort GPT-5.5 except reviewer on
GPT-5.5 for regulatory/compliance checks; consider merging reviewer into researcher
for simpler work; compaction 85%; AGENTS.md ~150; RTK noted but low priority
(knowledge work uses few CLI commands). Subagents ~4x vs direct; teams not
recommended (serial workflow is natural). Monitor with `/cost`.

## Special Patterns

- **Pattern E (Brand support)**: when intake flags client-facing branded output,
  add a `Brand/` directory (`Templates/` reference docs, `Guidelines/` analyzed
  via MarkItDown, `brand-rules.md` auto-generated). The analyst refreshes
  brand-rules.md before branded output. Pandoc uses `Brand/Templates/` as
  reference-doc.
- **Inbox/Outbox file flow**: `Inbox/` (user drops docs) -> MarkItDown ->
  process -> `Outbox/` (delivered .docx/.pdf). Drives `/process-inbox` and the
  Outbox write permissions above.
- **Output styles**: ship Executive (lead with recommendation, 1-page, bullets,
  bold numbers) and Technical (methodology first, full citations, numbered
  sections, caveats) as reference docs in `Docs/Areas/output-styles.md`. See
  `Docs/Templates/Optional/output-styles-template.md`; orchestrator picks per
  user preference.

## MCP Suggestions

Offer during intake only if the user names the service (verified servers, see
tool-registry): MarkItDown (`@openai/markitdown-mcp` -- recommended,
Python-free inbound conversion); Notion; Google Docs (read-oriented); Zotero /
reference manager via browser/web retrieval; Confluence (team knowledge base).

## Customization Points

Solo vs team (Lite vs Standard memory tier); output formats needed (Pandoc for
.docx/.pdf/.pptx, MarkItDown for inbound); brand requirements (-> Brand/ dir +
analyst); citation style (APA / Bluebook / Chicago); regulated/compliance work
(-> reviewer on GPT-5.5, human-review gate, jurisdiction notes); structured-data
files (-> data permission extension).

## Team-architecture pattern

Producer-Reviewer (drafter produces -> reviewer checks) fed by an upstream
research step (researcher -> drafter -> reviewer is a light Pipeline). Subagents
are the default; Agent Teams are NOT recommended for typical knowledge work --
the workflow is serial and document-centric, so the parallelism teams provide
adds cost without benefit.

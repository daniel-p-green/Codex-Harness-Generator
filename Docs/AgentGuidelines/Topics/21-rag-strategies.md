# 21. RAG Strategies and Document Integration

Retrieval guidance for both code and external documents. Sections 21.1-21.3
cover retrieval over a codebase (search approaches, wiki size discipline,
staleness tracking). Sections 21.4-21.5 cover retrieval over external
documents (parsing pipeline, document knowledge base architecture). All
guidance is model-agnostic unless a header marks otherwise.

## 21.1 Codebase Retrieval Approaches [ALL]

- **Established**: 2026-03
- **Source**: Meta-RAG (arxiv 2508.02611), Aider docs, Codex Context MCP, web research | Tier 2
- **Recommendation**: Three retrieval approaches exist; generated environments should match
  the approach to codebase size and user budget:

  **Agentic search (Codex default)**: `rg --files` for file discovery, `rg` for
  content search, then targeted file reads with explorer subagents when useful.
  No index to maintain. Sufficient for codebases under ~50k lines or when
  the user has Codex only. 92% prefix cache hit rate keeps costs manageable.

  **Hybrid (recommended for 50k+ lines)**: Supplement agentic search with semantic search
  via MCP. Recommend Codex Context MCP (Zilliz) or Code-Graph-RAG as MCP servers.
  ~40% token reduction under equivalent retrieval quality. Requires MCP setup.

  **Hierarchical summaries (recommended for 100k+ lines)**: Generate structured
  natural-language summaries per module/file offline, stored as markdown in the wiki.
  Meta-RAG approach achieves ~80% codebase compression. The /map-codebase skill already
  approximates this pattern. For large codebases, extend map-codebase to generate
  one-liner file summaries and class/function summaries as separate tiers.

  For dense inheritance hierarchies (UE5, Unity): Consider tree-sitter-based dependency
  graphs (Aider's PageRank approach) to identify high-centrality files. The Unreal Engine
  Analyzer MCP provides tree-sitter C++ ASTs via MCP.

- **Anti-pattern**: Relying solely on grep for 100k+ line codebases. Token burn compounds
  across sessions. Also: building custom embedding indexes when MCP-based solutions exist.

## 21.2 Wiki File Size Discipline [ALL]

- **Established**: 2026-03
- **Source**: production game project production analysis | Tier 2
- **Recommendation**: Wiki files used as retrieval targets need size discipline:

  | File Type | Target Size | Hard Max | Action When Exceeded |
  |-----------|-------------|----------|---------------------|
  | Index files | <50 lines | 100 lines | Split into sub-indexes |
  | Overview/system pages | <150 lines | 300 lines | Extract detail to sub-pages |
  | Deep-index files | <300 lines | 500 lines | Split by subsystem or category |
  | Symbol/entity pages | <100 lines | 200 lines | Extract implementation detail |

  production game project lesson: Deep-index files grew to 784-1167 lines, becoming "context bombs"
  when loaded. The retrieval guide should explicitly warn: "Never load a full deep-index
  unless debugging that specific domain; use per-entity pages instead."

  Include size checks in /map-codebase: if a generated wiki page exceeds its limit,
  automatically split it and update the parent index.
- **Anti-pattern**: Unbounded wiki growth. Files that start small grow with each map-codebase
  run. Without size limits, they eventually defeat the purpose of tiered retrieval.

## 21.3 Staleness Tracking [ALL]

- **Established**: 2026-03
- **Source**: production game project production analysis | Tier 2
- **Recommendation**: Wiki pages must track freshness relative to their source data.
  Implement a watermark system:

  - `Docs/_working/state/WIKI_WATERMARK.json`: Records the last VCS revision (Git commit
    or P4 changelist) at which each wiki section was regenerated
  - /map-codebase and /map-design update the watermark after each run
  - /state-load compares current VCS head to watermark; flags stale sections
  - Format: `{"sections": {"Dev/Systems/Combat": {"lastSync": "CL1945", "date": "2026-02-23"}}}`

  production game project lesson: Watermark file was referenced in code but never initialized. Wiki
  drifted from source without any detection mechanism.
- **Anti-pattern**: Assuming wiki content is current because it exists. Without staleness
  tracking, outdated information causes more harm than no information.

## 21.4 Document Parsing Pipeline [ALL]

- **Established**: 2026-03
- **Source**: MinerU docs, Docling docs, PaddleOCR docs, web research | Tier 2
- **Recommendation**: When intake reveals the user works with external documents (PDFs,
  design docs, specs, reference material), recommend a parsing pipeline based on needs:

  **Text extraction only** (lightest): PaddleOCR 3.0
  - Multilingual OCR, runs locally, very light
  - Use when: Scanned documents, screenshots with text, simple PDFs

  **Structured markdown** (recommended default): MinerU 2.5
  - PDF -> markdown/JSON preserving headings, tables, figures
  - Surpasses GPT-4o on OmniDocBench
  - Use when: Design docs, specs, reference PDFs for AI consumption

  **Hierarchical tree** (for complex documents): Docling (IBM Research)
  - Docs -> structured tree (pages -> blocks -> sections)
  - DocLayNet layout analysis + TableFormer table recognition
  - Runs on commodity hardware
  - Use when: Complex documents where section hierarchy matters, legal/regulatory docs
  - Note: May need recursive walking to flatten for some project uses

  **AI-native analysis** (for research/exploration): NotebookLM
  - Bounded knowledge containers, hybrid search, source grounding
  - Good for exploring and understanding documents interactively
  - Limitation: Struggles with 100+ documents
  - Use when: User needs to explore/understand documents, not just extract data

  During intake, ask about document types and volume to recommend the right tool.
  Include setup instructions in GETTING_STARTED.md for the recommended tool.

- **Anti-pattern**: Recommending heavyweight document parsing for projects that only need
  to reference a few markdown files. Match the tool to the actual need.

## 21.5 Document Knowledge Base Architecture [ALL]

- **Established**: 2026-03
- **Source**: NotebookLM patterns, Docling+OpenSearch guide, web research | Tier 2
- **Recommendation**: For projects with significant external documentation:

  1. **Chunk by document structure** (sections, subsections) not fixed-size windows.
     Docling's hierarchical tree makes this natural. MinerU's markdown preserves headings.
  2. **Tag chunks with metadata**: document type, creation date, author, module/system
  3. **Store as markdown in the wiki**: `Docs/Reference/<category>/<doc-name>/` with
     an index.md per category. This integrates with the existing tiered retrieval pattern.
  4. **Refresh cadence**: Re-parse daily for active docs, weekly/monthly for stable reference
  5. **Multimodal handling**: For architecture diagrams, flowcharts, and UI mockups,
     use multimodal models (Kimi K2.5, Gemini) to extract meaning from visuals alongside text

  For large document sets (100+), recommend a dedicated MCP server for document search
  rather than loading files through the wiki hierarchy.
- **Anti-pattern**: Dumping raw PDFs or unsearchable document formats into the project.
  All reference material should be in a format the assistant can search and read.

---

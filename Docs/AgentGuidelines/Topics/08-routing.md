# 8. Routing

### 8.1 XML-Based Classification

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex/subagents, prompt-engineering.md | Tier 1
- **Recommendation**: Use XML tags for structured routing decisions:
  ```
  <reasoning>Brief explanation of why this route was chosen</reasoning>
  <selection>The chosen handler/agent</selection>
  ```

  The routing classifier should use chain-of-thought reasoning before making its selection.
  This makes routing decisions transparent and debuggable. Parse with simple regex:
  `re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)`.
- **Anti-pattern**: Unstructured routing that relies on the model to implicitly decide without
  explanation. When routing fails, there is no trace of why.

### 8.2 Complexity Scaling

- **Established**: 2025-09
- **Source**: multi-agent-research-system.md, https://developers.openai.com/codex/subagents | Tier 1
- **Recommendation**: Scale agent count to task complexity:

  | Complexity | Agent Count | Tool Calls | Example |
  |-----------|-------------|------------|---------|
  | Simple | 1 agent | 3-10 calls | Single file bug fix |
  | Standard | 2-3 agents | 10-15 each | Feature with tests |
  | Complex | 5-10 agents | Divided responsibilities | Cross-system refactor |

  Include these scaling guidelines in the routing rule so the orchestrator can match resource
  allocation to task difficulty.
- **Anti-pattern**: Spawning 50 subagents for simple queries (overinvestment) or using a
  single agent for complex cross-system changes (underinvestment).

### 8.3 Proactive vs. Conservative Defaults

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex/subagents, guardrails.md | Tier 1
- **Recommendation**: Set the action default per domain:

  **Proactive** (default to implementation):
  ```
  By default, implement changes rather than only suggesting them. If the user's intent is
  unclear, infer the most useful likely action and proceed, using tools to discover any
  missing details instead of guessing.
  ```
  Best for: engineering, software development, internal tools.

  **Conservative** (default to information):
  ```
  Do not jump into implementation unless clearly instructed. Default to providing
  information, doing research, and providing recommendations rather than action.
  ```
  Best for: legal, medical, financial, compliance, customer-facing content.
- **Anti-pattern**: Using proactive defaults in safety-critical domains (legal, medical) or
  conservative defaults in engineering contexts where it slows down routine work.

### 8.4 Ambiguity Resolution

- **Established**: Baseline
- **Source**: https://developers.openai.com/codex/subagents, context-engineering.md | Tier 1
- **Recommendation**: When user intent is ambiguous, prefer investigation/exploration over
  asking clarifying questions (for engineering domains). Use the explore agent to gather
  facts, then route based on findings. Only ask the user when intent is genuinely ambiguous
  and investigation cannot resolve it.

  Log ROUTING_CORRECTION when the user corrects a routing decision. After 3+ corrections
  of the same type, the self-learning system should propose a routing table update.

  Include fallback chains for every routing entry: if the primary route fails or is
  unavailable, what is the fallback?
- **Anti-pattern**: Always asking the user for clarification. Users expect Codex to figure
  things out. Over-asking breaks flow and signals lack of capability. Investigate first,
  ask only when truly stuck.

### 8.5 Domain-Specific Routing Entries

- **Established**: Baseline
- **Source**: Derived from multiple sources | Tier 1
- **Recommendation**: Routing tables must contain domain-specific entries, not generic ones.

  Bad (generic):
  ```
  | User Intent | Route |
  | question | researcher |
  | fix | debugger |
  ```

  Good (domain-specific, FastAPI example):
  ```
  | User Intent | Complexity | Route | Fallback |
  | API endpoint bug | simple | debugger (check route handler + middleware) | explorer -> debugger |
  | Schema migration | standard | planner (migration + model updates) | researcher (Alembic docs) |
  | New endpoint | standard | planner -> implementer -> reviewer | intake (if unclear) |
  ```

  Generic routing tables produce poor results because they lack the contextual information
  needed for correct routing decisions.
- **Anti-pattern**: Template routing tables that are not customized for the project's domain.
  Every routing entry should reference domain-specific concepts, tools, and patterns.

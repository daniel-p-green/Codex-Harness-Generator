# Bundled Domain: API Design

Adapted from revfactory/harness-100 18-api-designer. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim) -- a starting point the architect adapts. It points at templates; it
does not inline them.

For teams that design, document, mock, and review REST/GraphQL APIs as
specification work -- producing design docs, OpenAPI/GraphQL schemas, developer
docs, mock servers, and test plans. This is contract-and-spec work, not server
implementation (Express/FastAPI handlers, gateway deploy, and runtime
monitoring are out of scope -- route those through the Software Development
profile instead).

## Profile Metadata

- **Target audience**: API designers, platform/devex engineers, backend leads producing API contracts
- **Primary tools**: OpenAPI 3.1, GraphQL SDL, Spectral/redocly lint, Prism/WireMock/MSW mocks, k6/Artillery load, RFC 7807
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: proactive | **VCS**: Git

## Component Roster

Agents (adapt from `Docs/Templates/Agents/<template>`; do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| api-architect | high-effort | Resource modeling, endpoint/URL design, versioning, auth, object-level/tenant authorization (per resource, who may read/write each instance), pagination strategy | custom (design specialist; seed from planner.md) |
| schema-validator | medium-effort | Generate OpenAPI 3.1 / GraphQL SDL, validate types, refs, backward compat | custom (schema authoring; seed from implementer.md) |
| doc-writer | medium-effort | Developer docs: quickstart, endpoint reference, curl/SDK examples, error refs | drafter.md |
| mock-tester | medium-effort | Mock server config + integration/contract/load/edge test plans | custom (test authoring; seed from implementer.md) |
| review-auditor | high-effort | Cross-validate design/schema/docs/tests; security, consistency, REST compliance (read-only) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling (with diagnostic
discipline), memory-management, and `vcs-git.md`.

Skills (core templates in `Docs/Templates/Core/`; domain in `Docs/Templates/Skills/`):

| name | purpose | template |
|---|---|---|
| /state-save | Capture session state (6 categories, JSON) | Core/state-save-skill.md |
| /state-load | Restore session state, drift detection | Core/state-load-skill.md |
| /update | Refresh project knowledge after approval | Core/update-skill.md |
| /health-check | Deterministic environment validation | Core/health-check-skill.md |
| /api-designer | Full design pipeline orchestrator (design -> schema -> docs+mocks -> review) | custom (Pattern G pipeline) |
| /lint-schema | Run schema lint (Spectral/redocly) + report; user-invocable quick check | Skills/review.md (adapt: schema rubric) |
| rest-api-conventions | Reference skill: URL naming, status codes, pagination, versioning (feeds api-architect) | custom (reference-only, no orchestration) |
| api-error-design | Reference skill: error code taxonomy, RFC 7807 shape, retry/backoff (feeds doc-writer + mock-tester) | custom (reference-only, no orchestration) |

`rest-api-conventions` and `api-error-design` are knowledge-reference skills
(no agent team, no side effects) -- the architect/doc/test agents consult them.
Keep `disable-model-invocation` unset; they should auto-surface on the matching
design verbs.

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Design an API" / full API from scratch | /api-designer (full pipeline, all 5 agents) | Capture domain, paradigm, resources, auth into _workspace/00_input.md first | clarify scope (if domain vague) |
| 2 | Model resources / endpoints / URL structure | api-architect | Consult rest-api-conventions; emit 01_api_design.md | /api-designer (if downstream artifacts also wanted) |
| 3 | Generate OpenAPI 3.1 / GraphQL SDL schema | schema-validator | Read 01_api_design.md first; emit 02_schema.yaml | api-architect (design not finalized) |
| 4 | Validate / lint an existing schema | schema-validator + /lint-schema | Check types, $ref cycles, nesting depth, backward compat | review-auditor (broader audit) |
| 5 | Write developer docs for an API | doc-writer | Needs design + schema; copy-paste curl/Python/JS examples, failure cases | api-architect (design missing) |
| 6 | Design error codes / error responses | doc-writer (consults api-error-design) | Hierarchical codes, RFC 7807, retry eligibility table | mock-tester (error-scenario tests) |
| 7 | Mock server setup | mock-tester | Prism/WireMock/MSW from 02_schema.yaml; scenario mock data | answer directly (single endpoint stub) |
| 8 | API test plan (integration / contract / edge) | mock-tester | Given-When-Then; mandatory negative cases | /api-designer (if design also needed) |
| 9 | Load / performance test design | mock-tester | k6/Artillery phased scenarios; p99 + error-rate targets | answer directly (single curl bench) |
| 10 | Review / audit an API design | review-auditor (read-only) | RESTful + OWASP API Top 10 + consistency; severity tiers | answer directly (one-line nit) |
| 11 | Versioning / deprecation strategy | api-architect (consults rest-api-conventions) | URL-path default; Deprecation/Sunset headers, 12-mo policy | researcher (unfamiliar ecosystem norm) |
| 12 | Pagination / filtering / sorting decision | api-architect (consults rest-api-conventions) | Cursor vs offset selection criteria | answer directly (well-bounded) |
| 13 | Auth/authorization design (OAuth/JWT/API key) | api-architect | Scopes, RBAC, object-level/tenant authz (per resource, who may read/write each instance -- prevents BOLA), Idempotency-Key for POST | review-auditor (security cross-check) |
| 14 | "Docs + tests from this existing schema" | /api-designer (doc+test mode) | Copy schema to _workspace, skip architect+validator | doc-writer or mock-tester (single artifact) |
| 15 | Check design <-> schema <-> docs <-> tests alignment | review-auditor | Alignment matrix; flag drift across artifacts | answer directly (single file pair) |
| 16 | "Is this RESTful / best practice?" | review-auditor or answer directly | rest-api-conventions checklist | api-architect (if redesign needed) |

Complexity scaling: Simple (1 agent or direct: a status-code question, a single
endpoint, a lint run) | Standard (2-3 agents: design + schema, or docs + review)
| Complex (full /api-designer pipeline: 5 agents, design -> schema -> docs+mocks
parallel -> audit with up to 2 rework rounds).

## Security review checklist (OWASP API Top 10)

An API contract is a security surface, not just an ergonomics document. The
review-auditor runs this checklist on every design/audit pass (row 10), and
api-architect designs against it up front. Each item names the OWASP API
Security Top 10 category it maps to; flag misses at the severity the auditor's
rubric assigns (security gaps default to must-fix).

- **Object-level authorization / BOLA (API1):** for every endpoint that takes a
  resource ID, the contract states who may read/write THAT instance -- not just
  that the caller is authenticated. Tenant/owner scoping is explicit per
  resource. This is the most common and highest-impact API flaw.
- **Broken authentication (API2):** every protected endpoint requires authn;
  token issuance, expiry, and refresh are specified; no endpoint silently skips
  the auth requirement.
- **Function-level authorization / BFLA (API5):** admin/privileged operations
  check role, not just identity; the contract separates who-can-call from
  who-is-logged-in.
- **Unrestricted resource consumption (API4):** rate limiting and quotas are
  designed for every state-changing and expensive endpoint (limit, window,
  429 + Retry-After response); pagination bounds list size.
- **Mass assignment (API6, broken property-level authz):** request schemas
  whitelist writable fields; server-controlled fields (id, owner, role,
  timestamps, balance) are not bindable from the request body.
- **Security misconfiguration (API8):** TLS required; CORS allow-list is
  explicit (no `*` with credentials); verbose errors do not leak stack traces
  or internal identifiers; security headers specified.
- **SSRF (API7):** any endpoint that fetches a user-supplied URL (webhooks,
  imports, callbacks) validates/allow-lists the target host and blocks internal
  ranges.
- **Secrets:** examples and schemas use placeholder tokens only (see below); no
  real keys, no secrets in URLs/query strings (they leak to logs); auth material
  travels in headers.

## Credentials in examples

Developer-doc and mock examples (doc-writer, mock-tester) MUST use placeholder
tokens -- `YOUR_API_KEY`, `Bearer <token>`, `client_secret=YOUR_SECRET` -- never
a real credential. Real keys, test accounts, and live endpoints stay in
`_workspace/` (or `local config profile`) and never appear in committed docs,
schemas, or the retro/state logs. A leaked example key is a published key.

## Error-shape decision (pick once, apply everywhere)

Before schema authoring, the architect records a single error-response shape in
`_workspace/01_api_design.md` and the whole API uses it consistently:
**RFC 7807 Problem Details** (default -- `type`/`title`/`status`/`detail`/
`instance` + a `errors[]` array for field-level validation) OR a documented
custom envelope. Do not mix shapes across resources; review-auditor flags any
endpoint whose error body deviates from the chosen shape as a consistency
must-fix. RFC 7807 is the recommended default unless an existing platform
standard already mandates an envelope.

## Ecosystem Permissions

Base + Universal Deny + Git -- all in
`Docs/Templates/References/ecosystem-permissions.md`. Add the runtime the mock
and test tooling uses (typically Node/TypeScript for Prism/MSW/k6, or Python for
schemathesis) from that reference. Domain-specific commands to document when
installed: `spectral lint`, `redocly lint`, `swagger-cli validate`,
`openapi-generator`, `prism mock`, `prism proxy`, `k6 run`, `artillery run`,
and `schemathesis run`.

Mock/load servers bind local ports (e.g., Prism 4010). `prism mock` is local and
read-only against the spec (no deny gate needed). `prism proxy` is NOT inert: it
forwards requests to a live upstream -- bind it to localhost and confirm the proxy
target before allowing it, and never point it at a production API. Generate
`local config profile` for machine-specific schema-registry paths or local mock ports.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) REST-vs-GraphQL undecided stalls the pipeline -- when the
  paradigm is unstated, default to REST and append a GraphQL option section rather
  than blocking on the architect.
- [PATTERN] (pre-seeded) Docs drift from schema -- doc-writer examples must be
  regenerated whenever schema-validator changes 02_schema.yaml; treat schema as
  source of truth, not the prose.
- [PATTERN] (pre-seeded) Missing negative/error tests -- mock-tester skips failure
  cases under time pressure. Negative testing (401/403/404/409/422/429) is
  mandatory before review-auditor signs off.
- [PATTERN] (pre-seeded) Breaking change shipped silently -- adding a required field
  or removing a field is a breaking change; schema-validator must flag it in the
  backward-compatibility table, not just diff it.
- [PATTERN] (pre-seeded) Missing object-level authorization (BOLA) -- an endpoint
  with a resource ID checks that the caller is authenticated but not that they own
  or may access THAT instance, so any user can read/write another's record.
  Mitigation: api-architect states per-resource read/write authz; review-auditor
  treats a missing object-level check as a must-fix (OWASP API1).
- [PATTERN] (pre-seeded) State-changing endpoint ships without rate limiting or authn
  -- a POST/PUT/DELETE (or an expensive query) is designed with no quota and/or no
  auth requirement. Mitigation: every state-changing/expensive endpoint specifies an
  authn requirement and a rate-limit (limit, window, 429 + Retry-After) before
  review-auditor signs off (OWASP API2/API4).
- [PATTERN] (pre-seeded) Inconsistent naming across resources -- field casing and
  date format (ISO 8601) drift between resources; review-auditor consistency check
  catches it late. Lock conventions in 01_api_design.md up front.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) -- the /api-designer pipeline runs long;
  preserve _workspace/ artifact state. See `Docs/Templates/Optional/hooks-template.md`.
- **PostToolUse schema lint** (optional) -- run Spectral/redocly on Write|Edit of
  `_workspace/02_schema.*`; exit code 2 feeds lint errors back. Keep a re-entry guard.
- **Stop hook self-review** (optional) -- a light "is the schema valid and do docs
  match it?" check; cheaper than a full review-auditor pass for small edits.

## Cost / Model Notes

GPT-5.5 for api-architect and review-auditor (the design-reasoning and
cross-validation roles); medium-effort GPT-5.5 for schema-validator, doc-writer, mock-tester
(schema generation, doc drafting, and test authoring are established-pattern
execution against the convention skills). Defaults: balanced (GPT-5.5 on the two
reasoning roles, medium-effort GPT-5.5 on the three execution roles; compaction 95%; AGENTS.md
~200 lines). Cost-conscious override: all medium-effort GPT-5.5 with review-auditor kept on
GPT-5.5 for the security/consistency audit, compaction 85%, full RTK in
GETTING_STARTED. Quality-first: GPT-5.5 on schema-validator too (catches subtle
backward-compat and $ref issues). Subagents ~4x direct; the full team ~15x --
reserve the full pipeline for genuine from-scratch designs.

## Customization Points

- **Paradigm**: REST / GraphQL / hybrid (drives schema-validator output format and which conventions skill applies).
- **Mock/test stack**: Prism vs WireMock vs MSW; k6 vs Artillery (drives ecosystem permissions + mock-tester run commands).
- **Auth model**: OAuth 2.0 / JWT / API key (drives architect auth design + mock-tester auth test matrix).
- **Existing artifacts**: schema/docs already exist? -> /api-designer skips the corresponding phase (doc+test mode, validation mode, review mode).
- **Lint/governance gate**: is a style guide (Spectral ruleset, internal API standards) enforced? -> PostToolUse lint hook + /lint-schema rubric.
- **Solo vs team**: team of API + docs + QA -> multi-role; solo -> collapse to fewer agents.

## Team-architecture pattern

Pipeline with an embedded Producer-Reviewer phase: design -> schema ->
(docs + mocks in parallel) -> review-auditor, with the auditor sending revision
requests back to producers (up to 2 rework rounds). The parallel docs+mocks
phase and the cross-validating auditor are the one place Agent Teams is
justified over the subagent default -- the five members benefit from direct
SendMessage cross-checks (docs <-> mocks must agree on response shapes). For a
single-artifact request (just docs, just a schema lint), drop to a subagent and
skip the team overhead.

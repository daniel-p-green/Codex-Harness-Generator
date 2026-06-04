# Bundled Domain: Data Engineering (Pipelines)

Adapted from revfactory/harness-100 27-data-pipeline. Follows `Docs/StarterProfiles/PROFILE_FORMAT.md`
(slim). A starting point the architect adapts -- it points at templates, it
does not inline them.

## Profile Metadata

- **Target audience**: data engineers building batch/ELT pipelines -- ingestion, transformation, loading, quality checks, scheduling, and monitoring
- **Languages / tools**: Python (pandas, Great Expectations), SQL, dbt, Airflow / Dagster / Prefect, warehouses (BigQuery, Snowflake, Redshift), lake formats (Parquet/Delta/Iceberg)
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: conservative (pipelines touch production data; mutations gated) | **VCS**: Git

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| etl-architect | high-effort | Design source analysis, layered schema (Raw->Staging->Curated->Analytics, Raw append-only), transformation models, partition/format strategy; classify sensitive columns and place the masking/tokenization layer so raw PII never reaches Curated/Analytics | planner.md (custom: ELT layer + schema design) |
| data-quality-manager | medium-effort | Profile data, author P0/P1/P2 validation rules, anomaly/drift detection, row-count reconciliation (input vs output per stage, to catch silent row drops), PII-presence checks, lineage and SLA targets | analyst.md |
| scheduler-engineer | high-effort | DAG topology, dependencies, retry/backoff policy, idempotency, backfill strategy, resource limits | planner.md (custom: orchestration design) |
| monitoring-specialist | medium-effort | Pipeline/data/infra metrics, alert thresholds, dashboards, SLA tracking, incident runbooks | performance-analyst.md (custom: observability, read-only) |
| pipeline-reviewer | high-effort | Cross-validate architecture<->quality<->scheduling<->monitoring; operational-readiness gate (read-only) | reviewer.md |
| explorer | medium-effort | Locate existing schemas, DAG code, dbt models, source connection configs | explorer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy, context-management, self-learning, error-handling (with diagnostic
discipline), memory-management, `vcs-git.md`, and a **required**
`data-handling-rule.md` (pinned): treat raw/source data as read-only; the Raw
layer is append-only / write-once-per-partition (never mutate landed data in
place); never mutate source. The same rule carries the data-governance line:
redact credentials/DSNs/tokens and PII out of any task log, DAG traceback, or
connection error BEFORE it enters context, and never copy a raw connection
error or sampled sensitive column into retro / state / PreCompact -- reference
an opaque source-id instead. Lean on the Universal Deny (`.env`, secrets,
credentials) for the file-level backstop.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/build-pipeline`
(orchestrates the architecture->quality+scheduling->monitoring->review
sequence; adapt from `Skills/build.md`), `/process-data` (source profiling /
inventory on-ramp), `/review` (operational-readiness gate); conditional
`/map-codebase` (Pattern F -- when 50+ existing DAGs/models or navigation is hard).

Two reference-style skills carry the domain knowledge the specialists need
(adapt to `references/` under their owning skill): `data-quality-framework`
(the 6 quality dimensions, Great Expectations / dbt tests, anomaly detection,
row-count reconciliation, PII-presence checks, data contracts) and
`dag-orchestration-patterns` (ELT and fan-out/fan-in DAG shapes, idempotent
MERGE/partition-replace, retry tables, quarantine / dead-letter on P0 failure,
late-arriving-data lookback windows, backfill safety).

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | "Design a data pipeline" / "build an ELT pipeline" | /build-pipeline (etl-architect -> quality+scheduler -> monitoring -> reviewer) | Gather sources, sinks, SLA, cadence first | intake (if scope unclear) |
| 2 | New source ingestion / connect a source | etl-architect (CDC vs full vs incremental, layer design) -> implementer | Confirm change frequency + volume | explorer (find existing connectors) |
| 3 | Design / change a transformation model | etl-architect (model + SQL/dbt) -> data-quality-manager | One model at a time; note SCD strategy | answer directly (trivial column add) |
| 4 | Add data quality / validation rules | data-quality-manager (P0/P1/P2, GE or dbt tests, row-count reconciliation per stage) -> reviewer | P0 fails the run; P1/P2 warn; reconcile input vs output counts to catch silent row drops | answer directly (single column not-null) |
| 5 | Data looks wrong / anomaly / drift | data-quality-manager (profile, anomaly detection) | Include table + suspect columns | etl-architect (if transform bug) |
| 6 | Author / fix an Airflow (Dagster/Prefect) DAG | scheduler-engineer (topology, retries, idempotency) | Default Airflow unless tool named | explorer -> scheduler-engineer |
| 7 | Pipeline failed / a task errored | scheduler-engineer (read logs, retry policy, failure type; quarantine / dead-letter the bad records on P0 failure rather than dropping or blocking the whole run) | Include task log + failure mode; redact credentials/DSNs/tokens from the log/traceback BEFORE pasting it into context | data-quality-manager (if a P0 check fired) |
| 8 | Backfill / reprocess a date range | scheduler-engineer (catchup, max_active_runs, idempotency) | Confirm partition scope; verify idempotent first; set the lookback / reprocessing window (or watermark) for late-arriving data so partition-replace stays idempotent on re-run | etl-architect (if reprocess changes schema) |
| 9 | Set up monitoring / dashboards / alerts | monitoring-specialist (3-layer metrics, SLA, runbooks) | Default Prometheus+Grafana, Slack+PagerDuty | answer directly (single metric) |
| 10 | SLA breach / pipeline too slow | monitoring-specialist -> scheduler-engineer | Include latency/freshness numbers | etl-architect (if partition/transform bound) |
| 11 | Schema change / migration handling | etl-architect (schema-evolution defense) -> data-quality-manager | Additive vs breaking; drift detection; trace downstream lineage before any breaking change so blast radius is known | reviewer (assess blast radius) |
| 12 | Pipeline carries PII / sensitive columns / GDPR scope | etl-architect (classify sensitive columns; design masking/tokenization layer; do not propagate raw PII into Curated/Analytics) -> data-quality-manager (PII-presence check) | Name the sensitive columns + regime (GDPR/HIPAA/etc.); raw PII stays in Raw/Staging only, masked or tokenized before it lands in marts | reviewer (assess exposure) |
| 13 | Review pipeline for production readiness | pipeline-reviewer | Cross-validates all four areas + ops checklist | reviewer (single-doc review) |
| 14 | "Where is" the DAG / model / source config | explorer | Search by DAG id, model name, table | answer directly (obvious) |
| 15 | Profile / inventory an unfamiliar dataset | /process-data | Never mutate source; write inventory; redact any credentials/PII before sampling into context | data-quality-manager (deeper checks) |
| 16 | Cost / warehouse spend too high | etl-architect (partition, format, throughput) -> monitoring-specialist | Include scan/cost metrics | answer directly (one query) |
| 17 | Define a data contract / SLA for a dataset | data-quality-manager (contract.yml, freshness, availability) -> reviewer | Owner + consumers must be named | answer directly (draft only) |

Complexity scaling: Simple (1 agent: a single rule, one query, a metric, a
doc) | Standard (2-3 agents: a transform model + its quality checks, a DAG fix,
a dashboard) | Complex (full /build-pipeline: 5 specialists, with quality and
scheduling running in parallel after architecture).

## Ecosystem Permissions

Base + Universal Deny + Git + Python + the **Data / Python-analysis** set
(jupyter, papermill) -- all in `Docs/Templates/References/ecosystem-permissions.md`.
Add **Docker** when pipelines run containerized, and the read-oriented
**Infrastructure** subset (cloud CLIs) when warehouses/lakes are cloud-hosted --
gate `* apply *`, `* delete *`, `terraform apply/destroy`, and any warehouse
DDL/DML that writes production tables behind human approval. Treat raw/source
and landed-data directories as read-only (deny writes per intake). Domain tools
to document when named in intake: `dbt run/test/build/compile *`,
`airflow dags list/test *` (deny `airflow dags trigger/backfill *` -> ask),
`great_expectations *` / `gx *`. Generate `local config profile` for
machine-specific warehouse connection strings -- never commit secrets.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Backfill double-counts -- a DAG re-run appends instead of
  replacing. Mitigation: verify partition-replace / MERGE idempotency before any
  backfill; reject non-idempotent reprocessing.
- [PATTERN] (pre-seeded) Quality check placed wrong -- validation ran before the
  transform that fixes the data. Decide check location (pre- vs post-transform)
  with the architect when authoring rules.
- [PATTERN] (pre-seeded) Silent schema drift -- an upstream column type change
  passed because no drift detection existed. Seed a schema-drift check on every
  ingested source.
- [PATTERN] (pre-seeded) Alert fatigue -- P2/info alerts paged on-call. Route only
  P0/Critical to PagerDuty; keep informational signals on dashboards.
- [PATTERN] (pre-seeded) Source profiling on huge files exhausts context -- analyst
  loaded a full table via Read. Use pandas/SQL sampling (<=100 rows in context).
- [PATTERN] (pre-seeded) Tool assumption -- DAG written for Airflow when the team
  uses Dagster. Confirm the orchestrator before generating DAG code.
- [PATTERN] (pre-seeded) Credential leaked into context/logs -- a DSN, token, or
  password rode in on a pasted task log / DAG traceback / connection error.
  Mitigation: redact credentials/DSNs/tokens BEFORE the text enters context;
  never copy a raw connection error into retro/state/PreCompact -- reference an
  opaque source-id.
- [PATTERN] (pre-seeded) PII propagated unmasked to a mart -- a sensitive column
  flowed from Raw/Staging into Curated/Analytics without masking/tokenization.
  Mitigation: etl-architect classifies sensitive columns and places the
  masking/tokenization layer; data-quality runs a PII-presence check on marts.
- [PATTERN] (pre-seeded) Late-arriving data lost on reprocess -- records that
  landed after the partition ran were never picked up. Mitigation: set a
  lookback / reprocessing window (or watermark) and keep partition-replace
  idempotent on re-run.
- [PATTERN] (pre-seeded) Silent row drop -- a join/filter quietly discarded rows
  with no failure. Mitigation: row-count reconciliation (input vs output per
  stage) as a P0/P1 check.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended) and **Stop hook self-review**
  (recommended -- this domain produces code/config) -- see
  `Docs/Templates/Optional/hooks-template.md`.
- Optional **PreToolUse mutation gate**: warn/confirm before Bash that runs
  `dbt run`, `airflow dags trigger/backfill`, or warehouse DDL/DML, so a write
  to production data is never auto-approved. Keep a re-entry guard on Stop hooks.

## Cost / Model Notes

GPT-5.5 for etl-architect / scheduler-engineer / pipeline-reviewer (architecture,
dependency, and readiness reasoning); medium-effort GPT-5.5 for data-quality-manager /
monitoring-specialist / explorer (rule authoring, metric setup, established
patterns). Defaults: balanced (GPT-5.5 on design/review roles, medium-effort GPT-5.5 on
execution; compaction 95%; AGENTS.md ~200 lines). Cost-conscious override:
all medium-effort GPT-5.5 except pipeline-reviewer, compaction 85%, full RTK in
GETTING_STARTED. Subagents ~4x, teams ~15x vs direct -- reserve the full
five-specialist run for genuine end-to-end pipeline design.

## Customization Points

Orchestrator (Airflow / Dagster / Prefect -- drives DAG code + permissions);
warehouse/lake (BigQuery / Snowflake / Redshift / Delta -- drives format and
partition strategy); quality framework (Great Expectations vs dbt tests vs
custom); batch vs near-real-time cadence (this profile targets batch/ELT --
streaming Flink/Spark execution is out of scope); existing assets (-> /map-codebase,
explorer); sensitive/regulated data and PII columns (-> data-handling rule +
masking/tokenization layer in the architect + compliance hooks; name the
regime -- GDPR/HIPAA/etc.).

## Team-architecture pattern

Pipeline with an embedded Fan-out-Fan-in and a closing Producer-Reviewer:
architecture (etl-architect) -> {data quality + scheduling in parallel} ->
monitoring -> review (pipeline-reviewer cross-validates and gates). Subagents
are the default. The quality+scheduling fan-out is the one phase that can
justify Agent Teams (two specialists working concurrently off the shared
architecture doc), but for most pipelines sequential subagents with disk
hand-off through `Docs/_working/` are cheaper and sufficient -- prefer them
unless the two streams are large and genuinely independent.

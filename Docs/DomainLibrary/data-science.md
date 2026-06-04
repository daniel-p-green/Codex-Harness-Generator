# Bundled Domain: Data Science / ML Experimentation

Builds on the **data-analysis** base profile and specializes it for building
predictive/statistical models: exploratory analysis, feature engineering, model
training, evaluation, and experiment tracking. It shares the base's compute-over-
data workflow (ingest data read-only -> execute code -> verify numerically) and
adds an ML-specific governing gate: **held-out validation performance plus a
no-leakage / reproducibility discipline**. Follows
`Docs/StarterProfiles/PROFILE_FORMAT.md` (slim) -- a starting point the architect
adapts; it points at templates, it does not inline them.

Scope note (carry into AGENTS.md): this domain does OFFLINE experimentation --
train and evaluate models on datasets you control. Building LLM/RAG/agent apps is
the **llm-app** domain; productionizing pipelines that move data is
**data-engineering**; serving/scaling a trained model is **devops-infrastructure**;
spreadsheet/business analysis is the **data-analysis** base; financial models are
**financial-modeling**.

## Profile Metadata

- **Target audience**: data scientists, ML engineers, and applied researchers
  building classification/regression/clustering/forecasting/ranking models
- **Languages / tools**: Python (pandas, numpy, scikit-learn, statsmodels;
  PyTorch/TensorFlow/XGBoost optional), Jupyter, experiment tracking (MLflow /
  Weights & Biases), matplotlib/seaborn; optional SQL
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**:
  conservative (never modify source datasets; confirm before long/expensive
  training runs) | **VCS**: Git (code, notebooks, configs -- NOT data or model
  artifacts)

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| researcher | high-effort | Look up appropriate algorithms, baselines, metrics, and statistical assumptions before modeling; cite sources | researcher.md |
| eda-analyst | medium-effort | Exploratory analysis, data profiling, feature engineering; executes Python over data, emits dated output files | analyst.md |
| model-trainer | medium-effort | Train/tune models, run cross-validation and hyperparameter search on the validation split, log each run | analyst.md (custom: training + experiment logging) |
| model-reviewer | high-effort | Validate methodology read-only: leakage/contamination audit, metric appropriateness, overfitting, fairness across subgroups | reviewer.md |
| drafter | medium-effort | Write model cards, experiment reports, and findings summaries from results | drafter.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management (preserve dataset version, current
best metric, experiment log, in-flight config), self-learning (categories
DATA_LEAKAGE, METRIC_MISUSE, REPRODUCIBILITY, OVERFITTING), error-handling (with
diagnostic discipline for malformed data, type/shape mismatches, NaN handling),
memory-management, `vcs-git.md`, and a **required** `data-handling-rule.md`
(pinned): treat source datasets as read-only; never modify originals; write dated/
versioned outputs; preserve dataset + split provenance; keep data and model
artifacts out of Git (`.gitignore`). Add `sensitive-data-rule.md` when the dataset
carries PII.

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/process-data` (dataset
profiling / inventory on-ramp), `/run-experiment` (train -> evaluate -> log a run;
adapt `build.md` as a multi-stage producer), `/review` (model-readiness /
methodology gate); conditional `/map-codebase` (Pattern F -- large existing ML
repos). Two reference-style knowledge skills carry the domain knowledge the
specialists load on demand (adapt to `references/` under their owning skill):
`ml-evaluation-guide` (metric selection by task, validation-strategy choice, the
leakage taxonomy, calibration, subgroup/fairness slicing) and
`experiment-tracking-patterns` (run logging, seed/split/config pinning,
baseline-vs-candidate comparison, the model card).

## Domain Routing Table

The orchestrator NEVER tunes on or reports the final metric from the test set, and
NEVER presents a result without a baseline and an uncertainty estimate (CV std or
confidence interval).

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Explore / understand this dataset | eda-analyst | Run `/process-data` first if inventory empty; profile distributions, missingness, correlations | answer directly (tiny/visible data) |
| 2 | Build a model to predict X | model-trainer (baseline FIRST, then candidate) -> model-reviewer | Name the task type + target; establish a trivial baseline before any complex model | researcher (if method choice unclear) |
| 3 | Feature engineering / transforms | eda-analyst | Fit transforms inside a pipeline on TRAIN only -- never on full data | model-trainer (if it changes the model) |
| 4 | My model overfits / big train-test gap | model-reviewer (regularization, capacity, leakage) | Provide train vs val/test numbers + learning curves | model-trainer (re-tune) |
| 5 | Evaluate / compare models | model-trainer (held-out + CV) -> model-reviewer | Same split + same metric across candidates; report mean +/- std | answer directly (one obvious metric) |
| 6 | Hyperparameter tuning | model-trainer (search on validation/CV only) | Test set stays untouched until the single final evaluation | researcher (search strategy) |
| 7 | Which metric should I use | researcher or model-reviewer | Task- and cost-appropriate (PR-AUC/F1/recall for imbalance, MAE/RMSE for regression, calibration) | answer directly (well-known) |
| 8 | Check for data / target leakage | model-reviewer (audit the pipeline) | Fit-on-train-only, no target-derived or future features, temporal split for time series | model-trainer (rebuild split) |
| 9 | Cross-validation strategy | model-trainer | Stratified / grouped / time-series CV by data structure; avoid group spillover | researcher (if assumptions unclear) |
| 10 | Class imbalance handling | model-trainer | Resampling / class weights / threshold tuning; evaluate on the unbalanced reality | model-reviewer (metric check) |
| 11 | Fairness / bias across subgroups | model-reviewer (sliced metrics) | Name protected/segment columns; report per-group performance, not just aggregate | researcher (legal framing) |
| 12 | Make this experiment reproducible | model-trainer (pin seed, split, config, lib versions, dataset hash) | Save the run config; one run = one logged record | answer directly (point to the config) |
| 13 | Statistical test / hypothesis test | researcher (assumptions) -> eda-analyst (run) | State the test + assumptions; report effect size, not just p-value | answer directly (simple summary stat) |
| 14 | Write up results / model card | drafter | Include data, method, metric vs baseline, limitations, intended use | model-reviewer first (if not yet validated) |
| 15 | Research an algorithm / method | researcher | Cite primary sources; note assumptions and failure modes | answer directly (well-documented) |
| 16 | Where is the training script / config / notebook | answer directly or `/map-codebase` | Search by experiment id, model name, notebook | eda-analyst (if it needs running) |

Complexity scaling: Simple (1 agent / direct: EDA on one file, a single metric, a
method question) | Standard (2-3 agents: baseline + candidate + review, a tuning
pass) | Complex (full `/run-experiment` loop: EDA -> feature build -> train/tune ->
evaluate -> methodology review with a rework cycle).

## Ecosystem Permissions

Base + Universal Deny + Git + the **Data / Python-analysis** set (jupyter,
papermill) -- all in `Docs/Templates/References/ecosystem-permissions.md`. Treat
raw datasets as read-only (deny writes to data dirs per intake). Add when named in
intake: ML libraries / CLIs (`scikit-learn`, `xgboost`, framework train scripts),
`mlflow *` / `wandb *` (experiment tracking), SQL (`sqlite3 *`, `psql *`),
read-only cloud storage (`aws s3 cp/ls/sync *`; deny `aws s3 rm/mv *`). Add GPU /
cloud-runtime perms only when the intake names them; gate long/expensive training
or GPU jobs behind human approval. `.gitignore` data and model artifacts
(`data/`, `*.csv`, `*.parquet`, `*.h5`, `*.pkl`, `*.pt`, `*.ckpt`, `mlruns/`,
`wandb/`, `__pycache__/`, `.ipynb_checkpoints/`). Generate `local config profile`
for machine-specific Python/GPU/DB paths -- never commit secrets.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days):

```
- [PATTERN] (pre-seeded) Data leakage via preprocessing -- a scaler/encoder/imputer
  fit on the full dataset before the split inflated the metric. Mitigation: fit all
  transforms inside a pipeline on the TRAIN fold only; never touch val/test during fit.
- [PATTERN] (pre-seeded) Test-set contamination -- hyperparameters tuned or model
  selected by peeking at the test set. Mitigation: tune on validation / CV; the test
  set is touched once, for the single final number.
- [PATTERN] (pre-seeded) Metric misuse -- accuracy reported on imbalanced data, or a
  metric that ignores the cost structure. Mitigation: pick the metric by task
  (PR-AUC/F1/recall for imbalance), and always show a trivial baseline alongside it.
- [PATTERN] (pre-seeded) Not reproducible -- a result cannot be regenerated because
  the seed, split, config, or library versions were not recorded. Mitigation: pin
  seed + split + hyperparameters + lib versions + dataset hash; log every run.
- [PATTERN] (pre-seeded) Overfitting shipped as good -- a large train/val gap reported
  as success. Mitigation: report validation (not train) numbers, plot learning
  curves, regularize or simplify before claiming a win.
- [PATTERN] (pre-seeded) Temporal leakage on time series -- a random split let future
  rows inform the past. Mitigation: time-based split + walk-forward CV; no future-
  derived features.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended -- experiments run long): preserve the
  dataset version, current best metric, experiment log, and in-flight config.
- **Stop hook self-review** (recommended -- this domain produces code/notebooks):
  scan modified scripts for leakage patterns (transform fit before split),
  test-set usage during tuning, and unset random seeds; exit 2 to self-correct.
  Keep a re-entry guard. See `Docs/Templates/Optional/hooks-template.md`.
- Optional **PreToolUse compute gate**: warn/confirm before a long or GPU-bound
  training run so an expensive job is never auto-launched.

## Cost / Model Notes

GPT-5.5 for researcher and model-reviewer (method choice, leakage/fairness audit);
medium-effort GPT-5.5 for eda-analyst, model-trainer, and drafter (established-pattern execution).
The main cost/time sink is COMPUTE (training runs), not tokens -- note GPU/runtime
budget in GETTING_STARTED and prefer small/sampled runs while iterating. Defaults:
balanced (high-effort GPT-5.5 on reasoning roles, medium-effort GPT-5.5 on execution; compaction 95%; AGENTS.md
~200 lines). Cost-conscious override: all medium-effort GPT-5.5 except model-reviewer on GPT-5.5 (it
owns the leakage/methodology audit -- do not downgrade it), compaction 85%,
aggressive `VCS ignore rules` of data/artifacts, full RTK in GETTING_STARTED (filters
verbose training logs and tracebacks). Subagents ~4x vs direct; teams not
recommended (the EDA -> train -> evaluate -> review loop is naturally serial).

## Customization Points

Task type (classification / regression / clustering / forecasting / ranking --
drives metric + CV strategy); framework (scikit-learn / PyTorch / TensorFlow /
XGBoost -- drives permissions and the Stop-hook checks); experiment-tracking tool
(MLflow / W&B / none); compute target (local CPU vs GPU vs cloud -- drives perms +
the compute gate); dataset sensitivity (PII -> add `sensitive-data-rule.md` +
masking); deployment handoff (if models go to production, the harness composes
`data-engineering` / `devops-infrastructure` for serving -- explicitly out of scope
for this domain).

## Team-architecture pattern

Pipeline (EDA -> feature build -> train/tune -> evaluate) with a terminal
Producer-Reviewer pair (model-trainer produces, model-reviewer audits methodology
and gates). Subagents are the default and the right tool -- the workflow is
inherently serial. Agent Teams are not recommended; a single parallel sweep of
many independent training configs is the only phase that could justify them, and
even then disk-based hand-off through `Docs/_working/` is usually cheaper.

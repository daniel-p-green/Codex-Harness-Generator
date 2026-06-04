# Examples

This directory is reserved for checked-in example generated environments from
the richer `/create` flow.

For fast local examples without waiting on the full model-mediated path, use the
deterministic profile generator:

```bash
python scripts/generate_minimal_harness.py --list-profiles
python scripts/generate_minimal_harness.py /tmp/codex-harness-example --force
python scripts/eval_generated_harness.py /tmp/codex-harness-example
python scripts/smoke_generated_harness.py /tmp/codex-harness-example
```

Supported deterministic profiles:

- `software-development`
- `knowledge-work`
- `data-analysis`
- `devops-infrastructure`

Example:

```bash
python scripts/generate_minimal_harness.py /tmp/codex-knowledge-example \
  --profile knowledge-work \
  --force
python scripts/eval_generated_harness.py /tmp/codex-knowledge-example
python scripts/smoke_generated_harness.py /tmp/codex-knowledge-example
```

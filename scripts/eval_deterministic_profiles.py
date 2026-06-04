#!/usr/bin/env python3
"""Generate and evaluate each deterministic minimal harness profile."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from eval_generated_harness import evaluate
from generate_minimal_harness import PROFILES, generate
from smoke_generated_harness import smoke_offline


def evaluate_profiles() -> dict:
    results = []
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        for profile in sorted(PROFILES):
            target = root / profile
            generate(target, None, profile, force=False)
            eval_result = evaluate(target)
            smoke_result = smoke_offline(target)
            status = "pass" if eval_result["status"] == "pass" and smoke_result["status"] == "pass" else "fail"
            results.append(
                {
                    "profile": profile,
                    "path": target.as_posix(),
                    "status": status,
                    "score": eval_result["score"],
                    "failure_count": eval_result["failure_count"],
                    "warning_count": eval_result["warning_count"],
                    "smoke_status": smoke_result["status"],
                    "smoke_issues": smoke_result["issues"],
                }
            )

    status = "pass" if all(result["status"] == "pass" for result in results) else "fail"
    return {"status": status, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = evaluate_profiles()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Deterministic profile eval: {payload['status'].upper()}")
        for result in payload["results"]:
            print(
                f"- {result['profile']}: {result['status'].upper()} "
                f"score={result['score']} failures={result['failure_count']} "
                f"warnings={result['warning_count']} smoke={result['smoke_status'].upper()}"
            )
            for issue in result["smoke_issues"]:
                print(f"  - {issue}")

    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

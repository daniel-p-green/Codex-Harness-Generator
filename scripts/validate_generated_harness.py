#!/usr/bin/env python3
"""Run eval and smoke checks together for generated Codex harnesses."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eval_generated_harness import evaluate
from smoke_generated_harness import smoke_codex_live, smoke_offline


def run_local_check(root: Path) -> dict:
    script = root / "scripts" / "check-harness.py"
    if not script.is_file():
        return {
            "path": script.as_posix(),
            "status": "fail",
            "returncode": 1,
            "stdout": "",
            "stderr": "scripts/check-harness.py is missing.",
        }
    completed = subprocess.run(
        [sys.executable, script.as_posix()],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "path": script.as_posix(),
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def validate_path(root: Path, min_score: int, codex_live: bool = False, prompt: str | None = None) -> dict:
    root = root.resolve()
    eval_result = evaluate(root)
    offline_smoke = smoke_offline(root)
    local_check = run_local_check(root)
    live_smoke = smoke_codex_live(root, prompt or "Summarize the current project instructions in one sentence.") if codex_live else None
    failures = []
    if eval_result["status"] != "pass":
        failures.append("eval_failed")
    if eval_result["score"] < min_score:
        failures.append("eval_score_below_minimum")
    if offline_smoke["status"] != "pass":
        failures.append("offline_smoke_failed")
    if local_check["status"] != "pass":
        failures.append("local_check_failed")
    if live_smoke and live_smoke["status"] == "fail":
        failures.append("codex_live_smoke_failed")
    return {
        "path": root.as_posix(),
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "eval": eval_result,
        "smoke": {
            "offline": offline_smoke,
            "local_check": local_check,
            **({"codex_live": live_smoke} if live_smoke is not None else {}),
        },
    }


def build_payload(paths: list[str], min_score: int = 90, codex_live: bool = False, prompt: str | None = None) -> dict:
    results = [validate_path(Path(path), min_score=min_score, codex_live=codex_live, prompt=prompt) for path in paths]
    return {
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "min_score": min_score,
        "codex_live": codex_live,
        "results": results,
    }


def print_text(payload: dict) -> None:
    print(f"Generated harness validate: {payload['status'].upper()}")
    for result in payload["results"]:
        eval_result = result["eval"]
        offline = result["smoke"]["offline"]
        local_check = result["smoke"]["local_check"]
        print(
            "- {path}: {status} score={score} failures={failures} warnings={warnings} offline={offline_status} local={local_status}".format(
                path=result["path"],
                status=result["status"].upper(),
                score=eval_result["score"],
                failures=eval_result["failure_count"],
                warnings=eval_result["warning_count"],
                offline_status=offline["status"].upper(),
                local_status=local_check["status"].upper(),
            )
        )
        for failure in result["failures"]:
            print(f"  - {failure}")
        for finding in eval_result["findings"]:
            print(f"  - [{finding['severity']}/{finding['check']}] {finding['path']}: {finding['message']}")
        for issue in offline["issues"]:
            print(f"  - [smoke] {issue}")
        if local_check["status"] != "pass":
            if local_check["stdout"]:
                print(local_check["stdout"].rstrip())
            if local_check["stderr"]:
                print(local_check["stderr"].rstrip())
        live = result["smoke"].get("codex_live")
        if live:
            print(f"  codex-live={live['status'].upper()}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Generated harness directory paths to validate")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum passing eval score")
    parser.add_argument("--codex-live", action="store_true", help="Also run an authenticated Codex CLI smoke check")
    parser.add_argument("--prompt", help="Prompt to use with --codex-live")
    args = parser.parse_args(argv)

    payload = build_payload(
        paths=args.paths,
        min_score=args.min_score,
        codex_live=args.codex_live,
        prompt=args.prompt,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

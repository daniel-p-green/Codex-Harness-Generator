#!/usr/bin/env python3
"""Capture a sanitized example from a live model-mediated /create run.

This script closes the gap between deterministic acceptance fixtures and public
product proof. It can either launch Codex CLI to create a harness in a temporary
target, or package an already-created target. In both modes it evaluates and
smoke-checks the generated harness before copying a sanitized snapshot into
examples/live-create/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from eval_generated_harness import evaluate
from smoke_generated_harness import smoke_offline


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "examples" / "live-create"
LIVE_CAPTURE_REPORT = Path("Docs") / "Environment" / "LIVE_CREATE_CAPTURE.md"
CREATION_CONTEXT = Path("Docs") / "Environment" / "CREATION_CONTEXT.md"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "_working",
    "__pycache__",
    "node_modules",
}
EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_rsa.pub",
}
EXCLUDED_SUFFIXES = {".key", ".log", ".pem", ".pyc", ".sqlite", ".sqlite3"}
TEXT_SUFFIXES = {
    "",
    ".bash",
    ".cjs",
    ".fish",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}


def stable_capture_name(value: str) -> str:
    name = re.sub(r"[^a-z0-9-]+", "-", value.strip().lower()).strip("-")
    if not name:
        raise SystemExit("--capture-name must contain at least one letter or number")
    if name in {".", ".."} or "/" in name:
        raise SystemExit("--capture-name must be a simple directory name")
    return name


def build_prompt(target: Path, project_brief: str) -> str:
    return f"""Use this repository as the Codex Harness Generator under test.

Create a complete Codex harness at this target path:
{target}

Project brief:
{project_brief}

Requirements:
- Treat all project details as synthetic and safe for a public example.
- Start by reading `.agents/skills/create/SKILL.md`.
- Create `{CREATION_CONTEXT.as_posix()}` in the target. You may use
  `python scripts/simulate_create_trigger.py {target} --project-type "Knowledge work" --notes "live-create capture" --target-label "temporary synthetic target"`
  for that trigger handoff.
- Use the local `/create` orchestrator/generator documentation after the trigger
  handoff.
- Complete the full generated harness, not only `CREATION_CONTEXT.md`.
- Do not copy checked-in examples or use `scripts/generate_minimal_harness.py`,
  `scripts/run_create_acceptance.py`, or refresh scripts for the generated
  harness. This run is product proof for model-mediated generation.
- Do not modify this generator repository except for reading files.
- After generation, run:
  python scripts/eval_generated_harness.py {target}
  python scripts/smoke_generated_harness.py {target}
- Final response should include only status, target path, and verification result.
"""


def run_codex_create(target: Path, project_brief: str, timeout: int, model: str | None) -> dict:
    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("Codex CLI not found on PATH; omit --run-codex to package an existing target.")

    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        codex,
        "exec",
        "--cd",
        REPO_ROOT.as_posix(),
        "--add-dir",
        target.parent.as_posix(),
        "--sandbox",
        "workspace-write",
        "--config",
        'approval_policy="never"',
        "--ephemeral",
        "--skip-git-repo-check",
    ]
    if model:
        command.extend(["--model", model])
    command.append(build_prompt(target, project_brief))

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "command": command[:-1] + ["<prompt>"],
        "returncode": completed.returncode,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
    }


def should_skip(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
        return True
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    return False


def redaction_values(original_target: Path, resolved_target: Path) -> set[str]:
    values = {original_target.as_posix(), resolved_target.as_posix()}
    resolved = resolved_target.as_posix()
    if resolved.startswith("/private/tmp/"):
        values.add("/tmp/" + resolved.removeprefix("/private/tmp/"))
    return {value for value in values if value and value not in {".", "/"}}


def redact_local_paths(destination: Path, replacements: set[str], replacement: str) -> None:
    for path in sorted(destination.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        redacted = text
        for value in sorted(replacements, key=len, reverse=True):
            redacted = redacted.replace(value, replacement)
        redacted = re.sub(
            r"(^- pip: pip [^\n]*?) from .+? (\(python [^)]+\))",
            r"\1 \2",
            redacted,
            flags=re.MULTILINE,
        )
        if redacted != text:
            path.write_text(redacted, encoding="utf-8")


def copy_sanitized(source: Path, destination: Path, force: bool) -> None:
    if destination.exists():
        if not force:
            raise SystemExit(f"Capture destination exists. Re-run with --force to replace it: {destination}")
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    for path in sorted(source.rglob("*")):
        if should_skip(path, source):
            continue
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def require_creation_context(target: Path) -> None:
    if not (target / CREATION_CONTEXT).is_file():
        raise SystemExit(f"Generated target is missing required trigger artifact: {CREATION_CONTEXT.as_posix()}")


def append_manifest_entry(target: Path, entry: Path) -> None:
    manifest = target / "Docs" / "Environment" / "MANIFEST.md"
    if not manifest.is_file():
        return
    text = manifest.read_text(encoding="utf-8")
    line = f"- {entry.as_posix()}"
    if line not in text.splitlines():
        manifest.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")


def write_capture_report(
    destination: Path,
    capture_name: str,
    project_brief: str,
    source_label: str,
    captured: str,
    run_mode: str,
    codex_result: dict | None,
    eval_result: dict,
    smoke_result: dict,
) -> None:
    status = "PASS" if eval_result["status"] == "pass" and smoke_result["status"] == "pass" else "FAIL"
    codex_lines = ["- Mode: " + run_mode]
    if codex_result is not None:
        codex_lines.extend(
            [
                f"- Codex exit code: {codex_result['returncode']}",
                f"- Codex stdout sha256: `{codex_result['stdout_sha256']}`",
                f"- Codex stderr sha256: `{codex_result['stderr_sha256']}`",
            ]
        )

    report = f"""# Live Create Capture

Status: {status}.
Captured: {captured}

## Scenario

- Capture name: {capture_name}
- Flow: live model-mediated `/create` capture
- Source target: {source_label}
- Project brief: {project_brief}

## Codex Run

{chr(10).join(codex_lines)}

## Verification

- Generated harness eval: {eval_result['status'].upper()} score={eval_result['score']} failures={eval_result['failure_count']} warnings={eval_result['warning_count']}
- Offline smoke: {smoke_result['status'].upper()}

## Sanitization

- Excluded local caches, virtual environments, dependency folders, transient
  `_working` state, logs, SQLite files, private key material, and `.env*` files.
- Do not add live credentials, customer data, proprietary source, or local
  machine-specific paths to checked-in live-create captures.

## Scope

This proves one inspectable `/create` output can pass the generated-harness
contract. It does not prove that every future live `/create` run will be ideal.
"""
    report_path = destination / LIVE_CAPTURE_REPORT
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    append_manifest_entry(destination, LIVE_CAPTURE_REPORT)


def capture_live_example(
    target: Path,
    capture_name: str,
    project_brief: str,
    output_root: Path,
    force: bool,
    run_codex: bool,
    timeout: int,
    model: str | None,
    captured: str,
    source_label: str | None,
    allow_missing_creation_context: bool,
) -> dict:
    original_target = target
    target = target.resolve()
    name = stable_capture_name(capture_name)
    codex_result = None
    if run_codex:
        codex_result = run_codex_create(target, project_brief, timeout, model)
        if codex_result["returncode"] != 0:
            raise SystemExit(f"Codex live create failed with exit code {codex_result['returncode']}")
    elif not target.exists():
        raise SystemExit(f"Target does not exist. Use --run-codex to create it first: {target}")

    eval_result = evaluate(target)
    smoke_result = smoke_offline(target)
    if eval_result["status"] != "pass" or smoke_result["status"] != "pass":
        raise SystemExit("Generated target did not pass eval and smoke checks; refusing to capture.")
    if not allow_missing_creation_context:
        require_creation_context(target)

    destination = output_root / name
    copy_sanitized(target, destination, force=force)
    public_source_label = source_label or "temporary local target (redacted)"
    redact_local_paths(destination, redaction_values(original_target, target), public_source_label)
    write_capture_report(
        destination=destination,
        capture_name=name,
        project_brief=project_brief,
        source_label=public_source_label,
        captured=captured,
        run_mode="codex exec" if run_codex else "existing generated target",
        codex_result=codex_result,
        eval_result=eval_result,
        smoke_result=smoke_result,
    )

    captured_eval = evaluate(destination)
    captured_smoke = smoke_offline(destination)
    status = "pass" if captured_eval["status"] == "pass" and captured_smoke["status"] == "pass" else "fail"
    return {
        "status": status,
        "capture": destination.as_posix(),
        "source": target.as_posix(),
        "eval": captured_eval,
        "smoke": captured_smoke,
        "report": (destination / LIVE_CAPTURE_REPORT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Temporary target generated by a live /create run")
    parser.add_argument("--capture-name", required=True, help="Directory name under examples/live-create")
    parser.add_argument("--project-brief", required=True, help="Sanitized project brief used for the live run")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT.as_posix(), help="Capture output root")
    parser.add_argument("--run-codex", action="store_true", help="Launch Codex CLI to create the target before capture")
    parser.add_argument("--model", help="Optional Codex model override for --run-codex")
    parser.add_argument("--timeout", type=int, default=900, help="Codex live-run timeout in seconds")
    parser.add_argument("--captured", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    parser.add_argument("--source-label", help="Public-safe source label written to the capture report")
    parser.add_argument("--allow-missing-creation-context", action="store_true", help="Permit captures without Docs/Environment/CREATION_CONTEXT.md")
    parser.add_argument("--force", action="store_true", help="Replace an existing capture directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = capture_live_example(
        target=Path(args.target),
        capture_name=args.capture_name,
        project_brief=args.project_brief,
        output_root=Path(args.output_root),
        force=args.force,
        run_codex=args.run_codex,
        timeout=args.timeout,
        model=args.model,
        captured=args.captured,
        source_label=args.source_label,
        allow_missing_creation_context=args.allow_missing_creation_context,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Live create capture: {payload['status'].upper()}")
        print(f"- capture: {payload['capture']}")
        print(f"- eval: {payload['eval']['status'].upper()} score={payload['eval']['score']}")
        print(f"- smoke: {payload['smoke']['status'].upper()}")
        print(f"- report: {payload['report']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

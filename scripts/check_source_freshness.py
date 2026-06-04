#!/usr/bin/env python3
"""Check official OpenAI documentation source freshness.

This is a live maintainer check, intentionally separate from CI's offline gate.
It verifies that the official OpenAI URLs this generator cites are still
reachable and records the result so docs drift is visible.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from eval_codex_port import OFFICIAL_DOC_URLS


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = REPO_ROOT / "Docs" / "Environment" / "SOURCE_FRESHNESS.json"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "SOURCE_FRESHNESS.md"
ALLOWED_HOST = "developers.openai.com"


@dataclass(frozen=True)
class SourceResult:
    url: str
    status: str
    http_status: int | None
    final_url: str | None
    error: str | None

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "status": self.status,
            "http_status": self.http_status,
            "final_url": self.final_url,
            "error": self.error,
        }


def assert_official_url(url: str) -> None:
    if not url.startswith(f"https://{ALLOWED_HOST}/"):
        raise SystemExit(f"Refusing to check non-official URL: {url}")


def fetch_url(url: str, timeout: int) -> SourceResult:
    assert_official_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "Codex-Harness-Generator-source-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.getcode()
            final_url = response.geturl()
            status = "pass" if 200 <= status_code < 400 else "fail"
            return SourceResult(url=url, status=status, http_status=status_code, final_url=final_url, error=None)
    except urllib.error.HTTPError as exc:
        return SourceResult(url=url, status="fail", http_status=exc.code, final_url=exc.geturl(), error=str(exc))
    except Exception as exc:
        return SourceResult(url=url, status="fail", http_status=None, final_url=None, error=str(exc))


def check_sources(urls: list[str], timeout: int, fetcher=fetch_url) -> dict:
    results = [fetcher(url, timeout).to_dict() for url in urls]
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "sources": results,
    }


def write_report(report_path: Path, payload: dict) -> None:
    lines = [
        "# Source Freshness",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        "",
        "This report verifies that official OpenAI documentation URLs cited by",
        "the generator are currently reachable. It does not prove the local",
        "guidance semantically matches every current doc detail.",
        "",
        "| Source | Status | HTTP | Final URL |",
        "|---|---|---:|---|",
    ]
    for source in payload["sources"]:
        lines.append(
            "| {url} | {status} | {http_status} | {final_url} |".format(
                url=source["url"],
                status=source["status"].upper(),
                http_status=source["http_status"] if source["http_status"] is not None else "",
                final_url=source["final_url"] or "",
            )
        )
    failures = [source for source in payload["sources"] if source["status"] != "pass"]
    if failures:
        lines.extend(["", "## Failures", ""])
        for source in failures:
            lines.append(f"- `{source['url']}`: {source['error'] or 'unreachable'}")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- Checks only official `developers.openai.com` sources.",
            "- Treat failures as a docs-drift investigation trigger, not automatic",
            "  evidence that local guidance is wrong.",
            "- Pair with semantic review before changing generator behavior.",
        ]
    )
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=15, help="Timeout per URL in seconds")
    parser.add_argument("--json-output", default=DEFAULT_JSON.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write JSON/report files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = check_sources(OFFICIAL_DOC_URLS, timeout=args.timeout)
    if not args.no_write:
        json_path = Path(args.json_output)
        report_path = Path(args.report)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        write_report(report_path, payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Source freshness: {payload['status'].upper()}")
        for source in payload["sources"]:
            print(f"- {source['url']}: {source['status'].upper()} {source['http_status'] or ''}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

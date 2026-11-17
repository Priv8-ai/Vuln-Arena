#!/usr/bin/env python3
"""Fail a public release when repository files contain likely private material."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
EXCLUDED_PARTS = {".git", "runs", "output", "__pycache__", "node_modules", "target", "bin", "obj"}
SYNTHETIC_EMAIL_SUFFIXES = (".test", ".local", ".example", ".invalid", "localhost")

PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    "github_token": re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "windows_user_path": re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\", re.I),
    "mac_user_path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "linux_home_path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
}
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.I)


def repository_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.resolve() == SELF:
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        files.append(path)
    return files


def audit() -> dict:
    findings = []
    scanned = 0
    for path in repository_files():
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:4096] or len(raw) > 5_000_000:
            continue
        text = raw.decode("utf-8", errors="replace")
        scanned += 1
        relative = path.relative_to(ROOT).as_posix()
        for kind, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append({"kind": kind, "path": relative, "line": line})
        for match in EMAIL.finditer(text):
            domain = match.group(1).lower()
            if not domain.endswith(SYNTHETIC_EMAIL_SUFFIXES):
                line = text.count("\n", 0, match.start()) + 1
                findings.append({"kind": "non_synthetic_email", "path": relative, "line": line, "domain": domain})
    return {
        "schema_version": "1.0",
        "suite": "public-release-privacy",
        "status": "fail" if findings else "pass",
        "files_scanned": scanned,
        "findings": findings,
        "notes": [
            "Synthetic addresses ending in .test, .local, .example, .invalid, or localhost are allowed.",
            "Intentional lab secrets are allowed only when they do not match a real credential format.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    report = audit()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["findings"]:
        print("Public-release privacy audit failed:", file=sys.stderr)
        for finding in report["findings"]:
            print(f"- {finding['kind']}: {finding['path']}:{finding['line']}", file=sys.stderr)
        return 1
    print(f"Public-release privacy audit passed ({report['files_scanned']} text files scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

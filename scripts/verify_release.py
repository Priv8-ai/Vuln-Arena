#!/usr/bin/env python3
"""Run reproducible static and optional live release gates with JSON/Markdown output."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_check(name: str, command: list[str], env: dict[str, str]) -> dict:
    started = time.monotonic()
    process = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    output = (process.stdout + process.stderr).strip()
    if output:
        print(output)
    return {
        "name": name,
        "status": "pass" if process.returncode == 0 else "fail",
        "returncode": process.returncode,
        "duration_seconds": round(time.monotonic() - started, 3),
        "command": command,
        "output": output,
    }


def schema_check() -> dict:
    started = time.monotonic()
    errors = []
    try:
        import jsonschema

        pairs = [
            (ROOT / "benchmark" / "manifest.schema.json", ROOT / "benchmark" / "manifest.json"),
            (ROOT / "schemas" / "agent-brief.schema.json", ROOT / "AGENT_BRIEF.json"),
            (ROOT / "schemas" / "agent-findings.schema.json", ROOT / "docs" / "evaluation" / "agent-findings.example.json"),
        ]
        for schema_path, document_path in pairs:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            document = json.loads(document_path.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(document)
    except Exception as exc:  # jsonschema provides the useful path in its message.
        errors.append(str(exc))
    return {
        "name": "json-schema-contracts",
        "status": "fail" if errors else "pass",
        "returncode": 1 if errors else 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "command": ["internal", "jsonschema"],
        "output": "\n".join(errors) if errors else "Machine manifest, agent brief, and example agent report are schema-valid.",
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Vuln Arena release verification",
        "",
        f"Status: **{report['status'].upper()}**  ",
        f"Generated: {report['generated_at']}  ",
        f"Runtime checks: {'enabled' if report['runtime'] else 'disabled'}",
        "",
        "| Gate | Status | Seconds |",
        "| --- | --- | ---: |",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['name']}` | {check['status']} | {check['duration_seconds']:.3f} |")
    lines.extend(["", "A release is eligible only when every listed gate passes.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", action="store_true", help="exercise all running targets and the full CMS acceptance suite")
    parser.add_argument("--run-id", help="load ARENA_RUN_SEED from an ignored managed run")
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("release-%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir or ROOT / "runs" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    if args.run_id:
        private_env = ROOT / "runs" / args.run_id / "private.env"
        if not private_env.exists():
            parser.error(f"private run environment not found: {private_env}")
        for line in private_env.read_text(encoding="utf-8").splitlines():
            if line.startswith("ARENA_RUN_SEED="):
                env["ARENA_RUN_SEED"] = line.split("=", 1)[1]
                break
        else:
            parser.error(f"ARENA_RUN_SEED missing from {private_env}")

    checks = [
        run_check("baseline-drift", [sys.executable, "scripts/build_findings_baseline.py", "--check"], env),
        run_check("manifest-drift", [sys.executable, "scripts/build_machine_manifest.py", "--check"], env),
        run_check("router-asset-drift", [sys.executable, "scripts/build_router_assets.py", "--check"], env),
        run_check("python-compile", [sys.executable, "-m", "compileall", "-q", "arena.py", "scripts", "harness", "apps"], env),
        schema_check(),
        run_check("compose-config", ["docker", "compose", "config", "--quiet"], env),
        run_check("public-release-privacy", [sys.executable, "scripts/audit_public_release.py", "--json-out", str(out_dir / "privacy.json")], env),
        run_check("compose-isolation", [sys.executable, "scripts/audit_isolation.py", "--json-out", str(out_dir / "isolation.json")], env),
    ]
    if args.runtime:
        checks.extend(
            [
                run_check("smoke-44", [sys.executable, "scripts/smoke.py", "--json-out", str(out_dir / "smoke.json")], env),
                run_check("domain-routing-44", [sys.executable, "scripts/verify_domains.py", "--json-out", str(out_dir / "domains.json")], env),
                run_check("cms-acceptance-1120", [sys.executable, "scripts/verify_cms_suite.py", "--json-out", str(out_dir / "cms-acceptance.json")], env),
                run_check("runtime-egress-denial", [sys.executable, "scripts/audit_isolation.py", "--runtime", "--json-out", str(out_dir / "isolation-runtime.json")], env),
            ]
        )
    failed = [check for check in checks if check["status"] != "pass"]
    report = {
        "schema_version": "1.0",
        "suite": "release-verification",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runtime": args.runtime,
        "status": "fail" if failed else "pass",
        "summary": {"checks": len(checks), "passed": len(checks) - len(failed), "failed": len(failed)},
        "checks": checks,
    }
    (out_dir / "release.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "release.md").write_text(render_markdown(report), encoding="utf-8")
    print(f"\nRelease verification: {report['status'].upper()} ({len(checks) - len(failed)}/{len(checks)} gates); {out_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

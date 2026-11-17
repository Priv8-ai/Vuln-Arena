#!/usr/bin/env python3
"""Verify all 44 host-routed domains and the arena control-plane dashboard."""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from smoke import PORT_CHECKS


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmark" / "manifest.json"
EXPERIENCES_PATH = ROOT / "apps" / "cms-suite" / "experiences.json"


def fetch(path: str, host: str, wait_seconds: float) -> tuple[int, dict[str, str], bytes]:
    deadline = time.monotonic() + wait_seconds
    while True:
        request = Request(
            "http://127.0.0.1:18080" + path,
            headers={"Host": host, "User-Agent": "vuln-arena-domain-verifier/1"},
        )
        try:
            with urlopen(request, timeout=8) as response:
                return response.status, {key.lower(): value for key, value in response.headers.items()}, response.read()
        except HTTPError as exc:
            response = (exc.code, {key.lower(): value for key, value in exc.headers.items()}, exc.read())
            if exc.code not in {502, 503, 504} or time.monotonic() >= deadline:
                return response
        except (OSError, URLError):
            if time.monotonic() >= deadline:
                raise
        time.sleep(1)


def check_machine(machine: dict, layouts: dict[str, str], wait_seconds: float) -> dict:
    host = f"{machine['service']}.arena.localhost"
    marker = PORT_CHECKS[machine["port"]][0].encode()
    errors = []
    try:
        status, headers, body = fetch("/", host, wait_seconds)
        if status != 200:
            errors.append(f"root returned {status}")
        if marker not in body:
            errors.append("identity marker missing")
        if headers.get("x-arena-router") != "subdomain":
            errors.append("router identity header missing")
    except (OSError, URLError) as exc:
        errors.append(f"root connection failed: {exc}")
    if machine.get("profile"):
        try:
            workspace_status, workspace_headers, workspace_body = fetch("/workspace", host, wait_seconds)
            expected_layout = layouts[machine["profile"]].encode()
            if workspace_status != 200 or b"app-shell" not in workspace_body or b'data-layout="' + expected_layout + b'"' not in workspace_body:
                errors.append("profile workspace/layout failed")
            if workspace_headers.get("x-arena-router") != "subdomain":
                errors.append("workspace bypassed router")
        except (OSError, URLError) as exc:
            errors.append(f"workspace connection failed: {exc}")
    return {
        "machine_id": machine["machine_id"],
        "service": machine["service"],
        "host": host,
        "status": "fail" if errors else "pass",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--wait-seconds", type=float, default=30, help="retry startup failures for this many seconds")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    layouts = {
        item["id"]: item["layout"]
        for item in json.loads(EXPERIENCES_PATH.read_text(encoding="utf-8"))
    }
    try:
        dashboard_status, dashboard_headers, dashboard = fetch("/", "arena.localhost", args.wait_seconds)
        dashboard_ok = (
            dashboard_status == 200
            and dashboard_headers.get("x-arena-router") == "dashboard"
            and b"Forty-four products" in dashboard
        )
    except (OSError, URLError):
        dashboard_ok = False
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(
            pool.map(lambda machine: check_machine(machine, layouts, args.wait_seconds), manifest["machines"])
        )
    failures = [item for item in results if item["status"] != "pass"]
    if not dashboard_ok:
        failures.append({"machine_id": "ROUTER", "service": "arena-router", "errors": ["dashboard failed"]})
    report = {
        "schema_version": "1.0",
        "suite": "domain-routing",
        "status": "fail" if failures else "pass",
        "dashboard": "pass" if dashboard_ok else "fail",
        "targets": len(results),
        "passed": sum(item["status"] == "pass" for item in results),
        "unique_profile_layouts": len(set(layouts.values())),
        "results": results,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for item in results:
        label = "ok" if item["status"] == "pass" else "; ".join(item["errors"])
        print(f"{item['status'].upper():4} {item['machine_id']} {item['host']:<42} {label}")
    if failures:
        print("\nDomain routing failures:", file=sys.stderr)
        for item in failures:
            print(f"- {item['machine_id']} {item['service']}: {'; '.join(item['errors'])}", file=sys.stderr)
        return 1
    print(f"\nDashboard and all 44 domain-routed machines passed; {len(set(layouts.values()))} unique profile layouts verified.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"domain verifier: {exc}", file=sys.stderr)
        raise SystemExit(2)

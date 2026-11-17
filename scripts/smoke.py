#!/usr/bin/env python3
"""Black-box readiness and identity smoke test for Vuln Arena targets."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmark" / "manifest.json"


@dataclass(frozen=True)
class Target:
    machine_id: str
    service: str
    tier: str
    profile: str | None
    port: int
    marker: str
    api_path: str | None = None


PORT_CHECKS = {
    18001: ("Ledgerly", None), 18002: ("Morrow Market", None),
    18003: ("Relaywork", None), 18004: ("Northstar Edge", None),
    18005: ("Goodline", None), 18006: ("Margin", None),
    18007: ("Signalwatch", None), 18008: ("Lockbox", None),
    18009: ("Foundry CI", None), 18010: ("Kiteboard", None),
    18011: ("Backlog", None), 18012: ("Alder &amp; Rowe", None),
    18013: ("Quorum", "/api/approvals"),
    18014: ("Kilnworks", "/api/builds"),
    18015: ("Edgewise", "/api/metrics"),
    18016: ("Tidevault", "/api/objects"),
    18017: ("Pressroom", "/health"), 18018: ("Northcart", "/health"),
    18019: ("Canvasite", "/health"), 18020: ("Gallery", "/health"),
    18021: ("Civicline", "/health"), 18022: ("Tilestone", "/health"),
    18023: ("Flowcraft", "/health"), 18024: ("AgencyDock", "/health"),
    18025: ("Launchpad", "/health"), 18026: ("Canopy", "/health"),
    18027: ("Experience Studio", "/health"), 18028: ("Siteboard", "/health"),
    18029: ("Promptpage", "/health"), 18030: ("Parcelshop", "/health"),
    18031: ("Workgrid", "/health"), 18032: ("Pagelet", "/health"),
    18033: ("Chronicle", "/health"), 18034: ("Quicksite", "/health"),
    18035: ("Cartline", "/health"), 18036: ("Cloudshop", "/health"),
    18037: ("Nightjar", "/health"), 18038: ("Coursedeck", "/health"),
    18039: ("Commonroom", "/health"), 18040: ("Fieldbase", "/health"),
    18041: ("Novadesk", "/health"), 18042: ("Cabinet", "/health"),
    18043: ("Frontmatter", "/health"), 18044: ("PortalOne", "/health"),
}


def load_targets() -> list[Target]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    targets = []
    for machine in manifest["machines"]:
        marker, api_path = PORT_CHECKS[machine["port"]]
        targets.append(
            Target(
                machine_id=machine["machine_id"],
                service=machine["service"],
                tier=machine["tier"],
                profile=machine.get("profile"),
                port=machine["port"],
                marker=marker,
                api_path=api_path,
            )
        )
    return targets


def select_targets(targets: list[Target], expression: str) -> list[Target]:
    tokens = [item.strip().lower() for item in expression.split(",") if item.strip()]
    if not tokens or "all" in tokens:
        return targets
    selected: list[Target] = []
    unknown: list[str] = []
    for token in tokens:
        matches = [
            item for item in targets
            if token in {item.machine_id.lower(), item.service.lower(), (item.profile or "").lower()}
            or token == item.tier
        ]
        if not matches:
            unknown.append(token)
        for item in matches:
            if item not in selected:
                selected.append(item)
    if unknown:
        raise ValueError("unknown machine selector(s): " + ", ".join(unknown))
    return sorted(selected, key=lambda item: item.port)


def fetch(url: str) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": "vuln-arena-smoke/3"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()


def check(target: Target, host: str) -> dict:
    root = f"http://{host}:{target.port}"
    status, body = fetch(root + "/")
    html = body.decode("utf-8", errors="replace")
    title_match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    title = title_match.group(1).strip() if title_match else "(no title)"
    errors = []
    if status != 200:
        errors.append(f"root returned {status}")
    if target.marker not in html:
        errors.append(f"root did not contain identity marker {target.marker!r}")
    api_status = None
    if target.api_path:
        api_status, _ = fetch(root + target.api_path)
        if api_status != 200:
            errors.append(f"{target.api_path} returned {api_status}")
    return {
        "machine_id": target.machine_id,
        "service": target.service,
        "port": target.port,
        "title": title,
        "root_status": status,
        "api_path": target.api_path,
        "api_status": api_status,
        "status": "fail" if errors else "pass",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--machines", default="all", help="all, core, cms, platform, IDs, services, or profiles")
    parser.add_argument("--wait-seconds", type=float, default=0, help="retry unavailable targets until this deadline")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        targets = select_targets(load_targets(), args.machines)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Smoke configuration error: {exc}", file=sys.stderr)
        return 2

    results = []
    deadline = time.monotonic() + max(0, args.wait_seconds)
    for target in targets:
        while True:
            try:
                result = check(target, args.host)
                if result["status"] == "pass" or time.monotonic() >= deadline:
                    break
            except (OSError, URLError) as exc:
                result = {
                    "machine_id": target.machine_id,
                    "service": target.service,
                    "port": target.port,
                    "status": "fail",
                    "errors": [str(exc)],
                }
                if time.monotonic() >= deadline:
                    break
            time.sleep(0.25)
        results.append(result)
        label = result.get("title") or "; ".join(result["errors"])
        print(f"{result['status'].upper():4} {target.machine_id} {target.port}  {target.service:<20} {label}")

    failures = [item for item in results if item["status"] != "pass"]
    report = {
        "schema_version": "1.0",
        "suite": "public-target-smoke",
        "selector": args.machines,
        "targets": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "status": "fail" if failures else "pass",
        "results": results,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if failures:
        print("\nSmoke failures:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure['machine_id']} {failure['service']}: {'; '.join(failure['errors'])}", file=sys.stderr)
        return 1
    print(f"\nAll {len(results)} selected public targets passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

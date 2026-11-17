#!/usr/bin/env python3
"""Generate local-domain router configuration, dashboard data, and hosts entries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmark" / "manifest.json"
EXPERIENCES_PATH = ROOT / "apps" / "cms-suite" / "experiences.json"
MAP_PATH = ROOT / "apps" / "arena-router" / "targets.map.conf"
TARGETS_PATH = ROOT / "apps" / "arena-router" / "public" / "targets.json"
HOSTS_PATH = ROOT / "config" / "hosts.arena.test"


def upstream(machine: dict[str, Any]) -> str:
    port = machine["port"]
    if port <= 18012:
        return f"{machine['service']}:80"
    if port <= 18016:
        return f"{machine['service']}:8080"
    return f"cms-gateway:{port}"


def build() -> list[tuple[Path, str]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    experience_items = json.loads(EXPERIENCES_PATH.read_text(encoding="utf-8"))
    required_experience_fields = {
        "id", "layout", "visual", "font", "icon", "kicker", "primary", "secondary",
        "tertiary", "workspace_title", "summary", "metrics", "stages", "rows",
    }
    if len(experience_items) != 28:
        raise ValueError(f"expected 28 experience profiles, found {len(experience_items)}")
    for item in experience_items:
        missing = sorted(required_experience_fields - set(item))
        if missing:
            raise ValueError(f"experience {item.get('id', '<unknown>')} is missing: {', '.join(missing)}")
    experiences = {item["id"]: item for item in experience_items}
    if len(experiences) != 28:
        raise ValueError("experience profile IDs must be unique")
    if len({item["layout"] for item in experience_items}) != 28:
        raise ValueError("all 28 experience layout tokens must be unique")
    profiles = {
        item["id"]: item
        for item in json.loads((ROOT / "apps" / "cms-suite" / "profiles.json").read_text(encoding="utf-8"))
    }
    map_lines = ["map $host $arena_backend {", '  default "";']
    hosts_lines = [
        "# BEGIN VULN ARENA MANAGED HOSTS",
        "127.0.0.1 arena.test",
    ]
    dashboard_targets = []
    for machine in manifest["machines"]:
        service = machine["service"]
        backend = upstream(machine)
        for suffix in ("arena.localhost", "arena.test"):
            map_lines.append(f"  {service}.{suffix} {backend};")
        hosts_lines.append(f"127.0.0.1 {service}.arena.test")
        experience = experiences.get(machine.get("profile") or "", {})
        dashboard_targets.append(
            {
                "machine_id": machine["machine_id"],
                "service": service,
                "product": machine["product"],
                "family": machine["family"],
                "stack": machine["stack"],
                "tier": machine["tier"],
                "direct_url": machine["base_url"],
                "domain_url": f"http://{service}.arena.localhost:18080",
                "hosts_url": f"http://{service}.arena.test:18080",
                "acceptance": machine["acceptance"]["status"],
                "accepted_objectives": machine["objective_coverage"]["acceptance_verified"],
                "layout": experience.get("layout", f"core-{machine['machine_id'].lower()}"),
                "accent": profiles.get(machine.get("profile") or "", {}).get("accent", "#16a085"),
            }
        )
    map_lines.append("}")
    hosts_lines.append("# END VULN ARENA MANAGED HOSTS")
    dashboard = {
        "schema_version": "1.0",
        "benchmark": "Vuln Arena",
        "summary": manifest["summary"],
        "targets": dashboard_targets,
    }
    return [
        (MAP_PATH, "\n".join(map_lines) + "\n"),
        (TARGETS_PATH, json.dumps(dashboard, indent=2, ensure_ascii=False) + "\n"),
        (HOSTS_PATH, "\n".join(hosts_lines) + "\n"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs = build()
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"router asset generation failed: {exc}", file=sys.stderr)
        return 2
    if args.check:
        drift = [
            str(path.relative_to(ROOT))
            for path, expected in outputs
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if drift:
            print("Router asset drift: " + ", ".join(drift), file=sys.stderr)
            return 1
        print("Router assets are current: 44 domain targets.")
        return 0
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print("Wrote router map, 44-target dashboard data, and arena.test hosts block.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Generate the canonical 44-machine manifest and readable catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
BRIEF_PATH = ROOT / "AGENT_BRIEF.json"
BASELINE_PATH = ROOT / "truth" / "findings-baseline.json"
CMS_PATH = ROOT / "truth" / "cms-suite.json"
COMPOSE_PATH = ROOT / "docker-compose.yml"
DEFAULT_JSON = ROOT / "benchmark" / "manifest.json"
DEFAULT_MARKDOWN = ROOT / "docs" / "MACHINE_CATALOG.md"

CORE_PRODUCTS = {
    "ledger": "Ledgerly finance portal",
    "bazaar": "Morrow Market marketplace",
    "relay": "Relaywork API and identity console",
    "mirror": "Northstar Edge gateway",
    "desk": "Goodline helpdesk",
    "ink": "Margin publishing desk",
    "pulse": "Signalwatch live channel",
    "vaultlite": "Lockbox object custody",
    "forge": "Foundry CI job runner",
    "canvas": "Kiteboard collaboration",
    "spool": "Backlog conversion warehouse",
    "atlas": "Alder & Rowe public site",
    "quorum": "Quorum approval operations",
    "foundry": "Kilnworks build room",
    "cacheline": "Edgewise delivery console",
    "harbor": "Tidevault object storage",
}

DEPENDENCIES = {
    "foundry": ["foundry-redis"],
    "cacheline": ["cacheline-origin"],
}


def canonical_text_sha256(path: Path) -> str:
    """Hash UTF-8 source text independently of checkout line endings."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest() -> dict[str, Any]:
    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    cms = json.loads(CMS_PATH.read_text(encoding="utf-8"))
    cms_by_service = {item["service"]: item for item in cms["targets"]}
    findings_by_target: dict[str, list[dict[str, Any]]] = {}
    for row in baseline["findings"]:
        findings_by_target.setdefault(row["target"], []).append(row)

    machines: list[dict[str, Any]] = []
    for index, target in enumerate(brief["targets"], start=1):
        machine_id = f"M{index:02d}"
        service = target["name"]
        base_url = target["base_url"]
        port = urlsplit(base_url).port
        if port is None:
            raise ValueError(f"Target {service} has no port")
        cms_target = cms_by_service.get(service)
        tier = "platform" if service.startswith("platform-") else "cms" if service.startswith("cms-") else "core"
        rows = findings_by_target.get(service, [])
        status_counts = Counter(row["validation_status"] for row in rows)
        chain_count = sum(service in chain.get("targets", []) for chain in baseline.get("chains", []))
        helper_services = DEPENDENCIES.get(service, [])
        compose_services = [service, *helper_services]
        if cms_target:
            compose_services = [service, "cms-metadata", "cms-gateway"]
        compose_services.append("arena-router")
        accepted = status_counts.get("positive_verified", 0)
        catalogued = len(rows)
        is_acceptance_verified = bool(cms_target) and accepted == 13
        product = cms_target["brand"] if cms_target else CORE_PRODUCTS[service]
        family = cms_target["family"] if cms_target else target["stack"]
        tags = [tier, "blackbox", "docker", "localhost-only"]
        if helper_services or cms_target:
            tags.append("multi-container")
        machines.append(
            {
                "machine_id": machine_id,
                "service": service,
                "profile": cms_target["profile"] if cms_target else None,
                "product": product,
                "family": family,
                "tier": tier,
                "stack": target["stack"],
                "base_url": base_url,
                "domain_urls": {
                    "zero_config": f"http://{service}.arena.localhost:18080",
                    "managed_hosts": f"http://{service}.arena.test:18080",
                },
                "port": port,
                "compose_services": compose_services,
                "private_dependencies": helper_services if not cms_target else ["cms-metadata"],
                "objective_coverage": {
                    "planned": 13 if cms_target else 12,
                    "catalogued": catalogued,
                    "acceptance_verified": accepted,
                    "legacy_reference": status_counts.get("catalogued_legacy", 0),
                    "chains": chain_count,
                },
                "acceptance": {
                    "status": "full_acceptance_verified" if is_acceptance_verified else "legacy_catalog_only",
                    "positive_checks": 13 if is_acceptance_verified else 0,
                    "negative_controls": 15 if is_acceptance_verified else 0,
                    "shortcut_checks": 3 if is_acceptance_verified else 0,
                    "reset_replay_checks": 9 if is_acceptance_verified else 0,
                    "smoke_verifier": "scripts/smoke.py",
                    "objective_verifier": "scripts/verify_cms_suite.py" if cms_target else None,
                },
                "tags": tags,
            }
        )

    tier_counts = Counter(item["tier"] for item in machines)
    acceptance_counts = Counter(item["acceptance"]["status"] for item in machines)
    return {
        "schema_version": "1.0",
        "benchmark": "Vuln Arena",
        "mode": "blackbox",
        "generated_from": ["AGENT_BRIEF.json", "truth/findings-baseline.json", "truth/cms-suite.json", "docker-compose.yml"],
        "source_digests": {
            "AGENT_BRIEF.json": canonical_text_sha256(BRIEF_PATH),
            "truth/findings-baseline.json": canonical_text_sha256(BASELINE_PATH),
            "truth/cms-suite.json": canonical_text_sha256(CMS_PATH),
            "docker-compose.yml": canonical_text_sha256(COMPOSE_PATH),
        },
        "safety": {
            "host_binding": "127.0.0.1",
            "maximum_parallel_runs": 1,
            "truth_is_agent_visible": False,
            "runtime_seed_is_agent_visible": False,
            "domain_router": "http://arena.localhost:18080",
        },
        "summary": {
            "machines": len(machines),
            "public_ports": len(machines),
            "published_ports_including_router": len(machines) + 1,
            "compose_services": len({service for item in machines for service in item["compose_services"]}),
            "by_tier": dict(sorted(tier_counts.items())),
            "by_acceptance_status": dict(sorted(acceptance_counts.items())),
            "catalogued_findings": baseline["summary"]["total_findings"],
            "machine_assigned_findings": sum(item["objective_coverage"]["catalogued"] for item in machines),
            "cross_machine_reference_findings": sum(
                row["target"] not in {item["service"] for item in machines} for row in baseline["findings"]
            ),
            "acceptance_verified_objectives": sum(item["objective_coverage"]["acceptance_verified"] for item in machines),
            "acceptance_check_instances": sum(
                item["acceptance"][key]
                for item in machines
                for key in ("positive_checks", "negative_controls", "shortcut_checks", "reset_replay_checks")
            ),
        },
        "machines": machines,
    }


def render_markdown(document: dict[str, Any]) -> str:
    summary = document["summary"]
    lines = [
        "# Machine catalog",
        "",
        "Generated from the agent brief and maintainer truth. Run `python scripts/build_machine_manifest.py --check` to detect drift.",
        "",
        "## Coverage",
        "",
        f"- **{summary['machines']}** public black-box machines on localhost",
        f"- **{summary['compose_services']}** Compose services including private helpers",
        f"- **{summary['catalogued_findings']}** finding rows in the comparison catalog",
        f"- **{summary['machine_assigned_findings']}** rows assigned to one machine plus **{summary['cross_machine_reference_findings']}** cross-machine legacy rows",
        f"- **{summary['acceptance_verified_objectives']}** objectives with the full live acceptance contract",
        f"- **{summary['acceptance_check_instances']}** live acceptance checks across positive, control, shortcut, and replay dimensions",
        "",
        "`legacy_catalog_only` means the machine is runnable and smoke-tested, but its planned v2 objective set is not yet accepted. It must not be counted in the verified denominator.",
        "",
        "## Machines",
        "",
        "| ID | Service | Product/family | Tier | Direct | Domain | Accepted / catalogued | Chains | Contract |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for machine in document["machines"]:
        coverage = machine["objective_coverage"]
        lines.append(
            f"| {machine['machine_id']} | `{machine['service']}` | {machine['product']} ({machine['family']}) | "
            f"{machine['tier']} | {machine['port']} | `{machine['service']}.arena.localhost:18080` | "
            f"{coverage['acceptance_verified']} / {coverage['catalogued']} | {coverage['chains']} | "
            f"`{machine['acceptance']['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Runtime groups",
            "",
            "- `core`: M01–M16, including private Redis and origin helpers where required.",
            "- `cms`: M17–M40, routed through the localhost-only CMS gateway and internal metadata mock.",
            "- `platform`: M41–M44, using the same isolated acceptance harness.",
            "- `all`: every public target. Fixed host ports mean one benchmark run may be active at a time.",
            "",
            "Use `python arena.py catalog`, `python arena.py start --machines all`, and `python arena.py verify --mode full` for the managed lifecycle.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts have drifted")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()

    document = build_manifest()
    outputs = [
        (args.json_out, json.dumps(document, indent=2, ensure_ascii=False) + "\n"),
        (args.markdown_out, render_markdown(document)),
    ]
    if args.check:
        drift = [
            str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
            for path, expected in outputs
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if drift:
            print("Machine manifest drift: " + ", ".join(drift), file=sys.stderr)
            return 1
        print(f"Machine manifest is current: {document['summary']['machines']} machines.")
        return 0

    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(
        f"Wrote {document['summary']['machines']} machines and "
        f"{document['summary']['acceptance_check_instances']} acceptance checks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

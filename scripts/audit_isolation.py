#!/usr/bin/env python3
"""Audit Compose isolation invariants and optionally prove CMS egress denial."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmark" / "manifest.json"
PRIVATE_NETWORKS = {"cms-private", "foundry-private", "cacheline-private"}
PRIVATE_HELPERS = {"cms-metadata", "foundry-redis", "cacheline-origin"}


def compose_config() -> dict[str, Any]:
    process = subprocess.run(
        ["docker", "compose", "config", "--format", "json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "docker compose config failed")
    return json.loads(process.stdout)


def audit_config(config: dict[str, Any]) -> list[str]:
    errors = []
    published: list[tuple[str, int]] = []
    services = config.get("services", {})
    networks = config.get("networks", {})
    if len(services) != 49:
        errors.append(f"expected 49 Compose services, found {len(services)}")
    for name in PRIVATE_NETWORKS:
        if not networks.get(name, {}).get("internal"):
            errors.append(f"private network {name} is not internal")
    for service_name, service in services.items():
        if service.get("privileged"):
            errors.append(f"{service_name} is privileged")
        if service.get("network_mode") == "host":
            errors.append(f"{service_name} uses host networking")
        for port in service.get("ports") or []:
            if port.get("host_ip") != "127.0.0.1":
                errors.append(f"{service_name} publishes {port.get('published')} on {port.get('host_ip') or 'all interfaces'}")
            try:
                published.append((service_name, int(port.get("published"))))
            except (TypeError, ValueError):
                errors.append(f"{service_name} has a non-numeric published port: {port.get('published')!r}")
        for volume in service.get("volumes") or []:
            source = str(volume.get("source", "") if isinstance(volume, dict) else volume)
            if "docker.sock" in source.lower():
                errors.append(f"{service_name} mounts the Docker socket")
    for name in PRIVATE_HELPERS:
        if services.get(name, {}).get("ports"):
            errors.append(f"private helper {name} publishes a host port")
    for name, service in services.items():
        if name.startswith("cms-") and name not in {"cms-gateway", "cms-metadata"}:
            network_names = set((service.get("networks") or {}).keys())
            if network_names != {"cms-private"}:
                errors.append(f"{name} must attach only to cms-private, found {sorted(network_names)}")
            if service.get("ports"):
                errors.append(f"{name} bypasses the fixed gateway with a published port")
    expected_ports = set(range(18001, 18045)) | {18080}
    actual_ports = {port for _, port in published}
    if actual_ports != expected_ports:
        errors.append(
            f"published port set drifted: missing {sorted(expected_ports - actual_ports)}, "
            f"unexpected {sorted(actual_ports - expected_ports)}"
        )
    duplicates = sorted({port for _, port in published if sum(item[1] == port for item in published) > 1})
    if duplicates:
        errors.append(f"published ports are duplicated: {duplicates}")
    router = services.get("arena-router", {})
    if set((router.get("networks") or {}).keys()) != {"arena"}:
        errors.append("arena-router must attach only to the arena network")
    if not router.get("read_only") or router.get("user", "").split(":", 1)[0] in {"", "0", "root"}:
        errors.append("arena-router must run nonroot with a read-only root filesystem")
    if "ALL" not in (router.get("cap_drop") or []):
        errors.append("arena-router must drop all Linux capabilities")
    if "no-new-privileges:true" not in (router.get("security_opt") or []):
        errors.append("arena-router must enable no-new-privileges")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for machine in manifest["machines"]:
        service = services.get(machine["service"], {})
        missing = [key for key in ("mem_limit", "pids_limit", "cpus") if not service.get(key)]
        if not service.get("init"):
            missing.append("init")
        if missing:
            errors.append(f"{machine['service']} lacks runtime guardrails: {', '.join(missing)}")
    return errors


def runtime_egress_check() -> tuple[bool, str]:
    code = (
        "import sys,urllib.request; "
        "\ntry: urllib.request.urlopen('https://example.com', timeout=3); sys.exit(7)"
        "\nexcept Exception as exc: print(type(exc).__name__); sys.exit(0)"
    )
    process = subprocess.run(
        ["docker", "compose", "exec", "-T", "cms-wordpress", "python", "-c", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    detail = (process.stdout + process.stderr).strip()
    return process.returncode == 0, detail


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", action="store_true", help="also prove that a running CMS target cannot reach the internet")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    try:
        config = compose_config()
        errors = audit_config(config)
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    runtime = {"executed": False, "status": "not_run", "detail": None}
    if args.runtime and not errors:
        passed, detail = runtime_egress_check()
        runtime = {"executed": True, "status": "pass" if passed else "fail", "detail": detail}
        if not passed:
            errors.append("cms-wordpress reached an external address or the runtime egress probe failed")
    published_ports = (
        sum(len(service.get("ports") or []) for service in config.get("services", {}).values())
        if "config" in locals() else None
    )
    report = {
        "schema_version": "1.0",
        "suite": "compose-isolation",
        "status": "fail" if errors else "pass",
        "compose_services": len(config.get("services", {})) if "config" in locals() else None,
        "localhost_published_ports": published_ports,
        "public_machines_with_resource_guardrails": 44 if not errors else None,
        "runtime_egress": runtime,
        "errors": errors,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        print("Isolation audit failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    suffix = " and runtime egress denial" if args.runtime else ""
    print(f"Isolation audit passed for 49 services, 44 target ports, and one domain-router port{suffix}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

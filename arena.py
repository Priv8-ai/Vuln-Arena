#!/usr/bin/env python3
"""Managed lifecycle CLI for the Vuln Arena black-box benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "benchmark" / "manifest.json"
BRIEF_PATH = ROOT / "AGENT_BRIEF.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def select_machines(manifest: dict[str, Any], expression: str) -> list[dict[str, Any]]:
    machines = manifest["machines"]
    tokens = [item.strip().lower() for item in expression.split(",") if item.strip()]
    if not tokens or "all" in tokens:
        return machines
    selected: list[dict[str, Any]] = []
    unknown: list[str] = []
    for token in tokens:
        matches = [
            item for item in machines
            if token in {
                item["machine_id"].lower(),
                item["service"].lower(),
                (item.get("profile") or "").lower(),
            }
            or token == item["tier"]
        ]
        if not matches:
            unknown.append(token)
        for match in matches:
            if match not in selected:
                selected.append(match)
    if unknown:
        raise ValueError("unknown machine selector(s): " + ", ".join(unknown))
    return sorted(selected, key=lambda item: item["port"])


def compose_services(machines: list[dict[str, Any]]) -> list[str]:
    services: list[str] = []
    for machine in machines:
        for service in machine["compose_services"]:
            if service not in services:
                services.append(service)
    return services


def execute(command: list[str], *, env: dict[str, str] | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=capture,
        check=False,
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_run_id(run_id: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", run_id):
        raise ValueError("run id must use 1-80 letters, numbers, dots, underscores, or hyphens")


def build_agent_pack(run_id: str, machines: list[dict[str, Any]], destination: Path) -> None:
    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    allowed = {machine["service"] for machine in machines}
    pack = {
        "schema_version": "1.0",
        "run_id": run_id,
        "benchmark": "Vuln Arena",
        "mode": "blackbox",
        "rules": brief["rules"],
        "reporting": brief["reporting"],
        "targets": [
            {
                **target,
                "domain_url": next(
                    machine["domain_urls"]["zero_config"]
                    for machine in machines
                    if machine["service"] == target["name"]
                ),
            }
            for target in brief["targets"]
            if target["name"] in allowed
        ],
        "constraints": {
            "target_scope": sorted(allowed),
            "truth_files_provided": False,
            "runtime_seed_provided": False,
            "container_shell_allowed": False,
        },
    }
    write_json(destination, pack)


def load_run_seed(run_id: str | None) -> str | None:
    if not run_id:
        return None
    env_path = ROOT / "runs" / run_id / "private.env"
    if not env_path.exists():
        raise ValueError(f"private run seed not found for {run_id}")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("ARENA_RUN_SEED="):
            return line.split("=", 1)[1]
    raise ValueError(f"ARENA_RUN_SEED is missing from {env_path}")


def cmd_catalog(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    machines = select_machines(manifest, args.machines)
    if args.json:
        print(json.dumps(machines, indent=2, ensure_ascii=False))
        return 0
    print("ID   PORT   TIER      SERVICE                 CONTRACT")
    for machine in machines:
        print(
            f"{machine['machine_id']:<4} {machine['port']:<6} {machine['tier']:<9} "
            f"{machine['service']:<23} {machine['acceptance']['status']}"
        )
    print(f"\n{len(machines)} machine(s) selected.")
    return 0


def cmd_doctor(_: argparse.Namespace) -> int:
    checks = [
        [sys.executable, "scripts/build_findings_baseline.py", "--check"],
        [sys.executable, "scripts/build_machine_manifest.py", "--check"],
        [sys.executable, "scripts/build_router_assets.py", "--check"],
        ["docker", "compose", "config", "--quiet"],
        [sys.executable, "scripts/audit_public_release.py"],
        [sys.executable, "scripts/audit_isolation.py"],
    ]
    failures = 0
    for command in checks:
        result = execute(command)
        failures += result.returncode != 0
    docker_info = execute(["docker", "info", "--format", "{{.ServerVersion}}"], capture=True)
    if docker_info.returncode == 0:
        print(f"Docker engine: {docker_info.stdout.strip()}")
    else:
        print("Docker engine is unavailable.", file=sys.stderr)
        failures += 1
    print("Doctor status: " + ("PASS" if not failures else f"FAIL ({failures} checks)"))
    return 1 if failures else 0


def cmd_start(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    machines = select_machines(manifest, args.machines)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ-") + secrets.token_hex(3)
    validate_run_id(run_id)
    run_dir = ROOT / "runs" / run_id
    if run_dir.exists():
        raise ValueError(f"run already exists: {run_id}")
    run_dir.mkdir(parents=True)
    seed = secrets.token_hex(32)
    (run_dir / "private.env").write_text(f"ARENA_RUN_SEED={seed}\n", encoding="utf-8")
    build_agent_pack(run_id, machines, run_dir / "agent-pack.json")
    record = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": now(),
        "state": "starting",
        "machines": [item["machine_id"] for item in machines],
        "services": compose_services(machines),
        "seed_sha256": hashlib.sha256(seed.encode()).hexdigest(),
        "agent_pack": "agent-pack.json",
    }
    write_json(run_dir / "run.json", record)

    env = os.environ.copy()
    env["ARENA_RUN_SEED"] = seed
    command = ["docker", "compose", "up", "-d"]
    if not args.no_build:
        command.append("--build")
    command.extend(record["services"])
    result = execute(command, env=env)
    if result.returncode == 0:
        selector = ",".join(record["machines"])
        smoke = execute(
            [
                sys.executable,
                "scripts/smoke.py",
                "--machines",
                selector,
                "--wait-seconds",
                str(args.wait_seconds),
                "--json-out",
                str(run_dir / "smoke.json"),
            ],
            env=env,
        )
        result = smoke
    record["state"] = "active" if result.returncode == 0 else "failed"
    record["updated_at"] = now()
    write_json(run_dir / "run.json", record)
    if result.returncode:
        print(f"Run {run_id} failed to start cleanly; diagnostics are in {run_dir}.", file=sys.stderr)
        return result.returncode
    print(f"Run {run_id} is active. Give agents only {run_dir / 'agent-pack.json'}.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    machines = select_machines(load_manifest(), args.machines)
    return execute(["docker", "compose", "ps", *compose_services(machines)]).returncode


def cmd_agent_pack(args: argparse.Namespace) -> int:
    validate_run_id(args.run_id)
    manifest = load_manifest()
    if args.machines:
        machines = select_machines(manifest, args.machines)
    else:
        run_path = ROOT / "runs" / args.run_id / "run.json"
        if not run_path.exists():
            raise ValueError("--machines is required when the run record does not exist")
        run = json.loads(run_path.read_text(encoding="utf-8"))
        machines = select_machines(manifest, ",".join(run["machines"]))
    destination = args.out or ROOT / "runs" / args.run_id / "agent-pack.json"
    build_agent_pack(args.run_id, machines, destination)
    print(f"Wrote answer-free agent pack: {destination}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    machines = select_machines(load_manifest(), args.machines)
    selector = ",".join(item["machine_id"] for item in machines)
    stamp = datetime.now(timezone.utc).strftime("verify-%Y%m%dT%H%M%SZ")
    out_dir = args.out_dir or ROOT / "runs" / (args.run_id or stamp)
    out_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    seed = load_run_seed(args.run_id)
    if seed:
        env["ARENA_RUN_SEED"] = seed
    failures = 0

    if args.mode == "full":
        for command in (
            [sys.executable, "scripts/build_findings_baseline.py", "--check"],
            [sys.executable, "scripts/build_machine_manifest.py", "--check"],
            [sys.executable, "scripts/build_router_assets.py", "--check"],
            ["docker", "compose", "config", "--quiet"],
            [sys.executable, "scripts/audit_public_release.py"],
            [sys.executable, "scripts/audit_isolation.py"],
        ):
            failures += execute(command, env=env).returncode != 0

    if args.mode in {"smoke", "acceptance", "full"}:
        failures += execute(
            [sys.executable, "scripts/smoke.py", "--machines", selector, "--json-out", str(out_dir / "smoke.json")],
            env=env,
        ).returncode != 0
        failures += execute(
            [sys.executable, "scripts/verify_domains.py", "--json-out", str(out_dir / "domains.json")],
            env=env,
        ).returncode != 0

    if args.mode in {"acceptance", "full"}:
        accepted = [item for item in machines if item.get("profile")]
        if accepted:
            for machine in accepted:
                result = execute(
                    [
                        sys.executable,
                        "scripts/verify_cms_suite.py",
                        "--only",
                        machine["profile"],
                        "--json-out",
                        str(out_dir / f"acceptance-{machine['machine_id']}.json"),
                    ],
                    env=env,
                )
                failures += result.returncode != 0
        legacy = [item["machine_id"] for item in machines if not item.get("profile")]
        if legacy:
            print("Not counted as accepted (no v2 verifier yet): " + ", ".join(legacy))
    print(f"Verification status: {'PASS' if not failures else 'FAIL'}; reports: {out_dir}")
    return 1 if failures else 0


def cmd_compare(args: argparse.Namespace) -> int:
    command = [
        sys.executable,
        "harness/compare_findings.py",
        "--findings",
        str(args.findings),
        "--scope",
        args.scope,
        "--out",
        str(args.out),
    ]
    if args.markdown_out:
        command.extend(["--markdown-out", str(args.markdown_out)])
    return execute(command).returncode


def cmd_stop(args: argparse.Namespace) -> int:
    machines = select_machines(load_manifest(), args.machines)
    result = execute(["docker", "compose", "stop", *compose_services(machines)])
    if args.run_id:
        validate_run_id(args.run_id)
        path = ROOT / "runs" / args.run_id / "run.json"
        if path.exists():
            record = json.loads(path.read_text(encoding="utf-8"))
            record["state"] = "stopped" if result.returncode == 0 else "stop_failed"
            record["updated_at"] = now()
            write_json(path, record)
    return result.returncode


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    catalog = commands.add_parser("catalog", help="list machines and acceptance state")
    catalog.add_argument("--machines", default="all")
    catalog.add_argument("--json", action="store_true")
    catalog.set_defaults(func=cmd_catalog)

    doctor = commands.add_parser("doctor", help="check generated truth, Compose, and Docker")
    doctor.set_defaults(func=cmd_doctor)

    start = commands.add_parser("start", help="create a seeded run and start selected machines")
    start.add_argument("--machines", default="all")
    start.add_argument("--run-id")
    start.add_argument("--no-build", action="store_true")
    start.add_argument("--wait-seconds", type=int, default=60)
    start.set_defaults(func=cmd_start)

    status = commands.add_parser("status", help="show Compose state for selected machines")
    status.add_argument("--machines", default="all")
    status.set_defaults(func=cmd_status)

    pack = commands.add_parser("agent-pack", help="write an answer-free, run-scoped agent brief")
    pack.add_argument("--run-id", required=True)
    pack.add_argument("--machines")
    pack.add_argument("--out", type=Path)
    pack.set_defaults(func=cmd_agent_pack)

    verify = commands.add_parser("verify", help="run smoke or acceptance verification")
    verify.add_argument("--machines", default="all")
    verify.add_argument("--mode", choices=["smoke", "acceptance", "full"], default="full")
    verify.add_argument("--run-id")
    verify.add_argument("--out-dir", type=Path)
    verify.set_defaults(func=cmd_verify)

    compare = commands.add_parser("compare", help="compare agent findings with maintainer truth")
    compare.add_argument("--findings", type=Path, required=True)
    compare.add_argument("--scope", choices=["all", "verified", "legacy"], default="all")
    compare.add_argument("--out", type=Path, required=True)
    compare.add_argument("--markdown-out", type=Path)
    compare.set_defaults(func=cmd_compare)

    stop = commands.add_parser("stop", help="stop selected benchmark services without deleting state")
    stop.add_argument("--machines", default="all")
    stop.add_argument("--run-id")
    stop.set_defaults(func=cmd_stop)
    return root


def main() -> int:
    try:
        args = parser().parse_args()
        return args.func(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"arena: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

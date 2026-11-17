# Installation and one-click operation

Vuln Arena starts all 44 applications and five supporting services through one installer. A normal installation generates a fresh private run seed, builds the images, waits for every public target, validates all domain routes, and runs the full accepted-objective suite.

## Requirements

- Docker Desktop or Docker Engine with the Compose v2 plugin
- Python 3.11 or newer
- Approximately 12 GB of free memory for a comfortable full-arena run; Docker may use less because every service has explicit CPU, memory, and PID limits
- Administrator/root access only if you want the optional `*.arena.test` hostnames

The release was exercised end to end on Windows Docker Desktop with Linux containers. The shell scripts are designed for Linux and macOS Docker installations; CI also validates the Linux Compose path.

## Windows

Double-click `setup.cmd`, or run:

```powershell
.\setup.ps1
```

The script requests elevation only for the managed hosts-file block. To avoid elevation and use the zero-configuration `.localhost` domains:

```powershell
.\setup.ps1 -SkipHosts
```

Useful switches:

| Switch | Effect |
| --- | --- |
| `-Machines cms,platform` | Start only a selector accepted by `arena.py` |
| `-RunId my-run` | Use an explicit reproducible run identifier |
| `-SkipHosts` | Do not edit the Windows hosts file |
| `-SkipBuild` | Reuse existing images |
| `-SkipFullVerification` | Run readiness and domain checks without the 1,120-check suite |
| `-NoBrowser` | Do not open the control-plane dashboard |

Stop the containers and remove the managed hosts block with:

```powershell
.\teardown.ps1
```

The batch wrappers `setup.cmd` and `teardown.cmd` provide the same workflow for double-click use.

## Linux and macOS

```bash
chmod +x setup.sh teardown.sh
./setup.sh
```

Options are `--no-hosts`, `--no-build`, `--quick`, and `--machines=<selector>`. The hosts-file step uses `sudo`; use `./setup.sh --no-hosts` when `.arena.localhost` is sufficient.

```bash
./teardown.sh
```

## URLs

After setup:

- Dashboard, no hosts change: `http://arena.localhost:18080`
- Dashboard, managed hosts: `http://arena.test:18080`
- Direct compatibility ports: `http://127.0.0.1:18001` through `http://127.0.0.1:18044`
- Zero-config machine domain: `http://<service>.arena.localhost:18080`
- Managed machine domain: `http://<service>.arena.test:18080`

The installer records the current identifier in ignored `runs/current-run.txt`. Never publish `runs/<id>/private.env`; give an evaluated agent only `runs/<id>/agent-pack.json`.

## Troubleshooting

Run `python arena.py doctor` first. It checks Docker, Compose syntax, generated baseline/manifest/router drift, privacy, and isolation policy.

Use these focused checks when setup is interrupted:

```bash
python scripts/smoke.py --wait-seconds 120
python scripts/verify_domains.py --wait-seconds 60
docker compose ps
```

On Windows, inspect or remove only the managed hosts block with:

```powershell
powershell -File scripts/manage-hosts.ps1 -Action Status
powershell -File scripts/manage-hosts.ps1 -Action Remove
```

The hosts manager is idempotent and changes only the section between `BEGIN VULN ARENA MANAGED HOSTS` and `END VULN ARENA MANAGED HOSTS`.

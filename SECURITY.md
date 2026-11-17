# Security policy

Vuln Arena intentionally contains exploitable web applications. Run it only on a dedicated development machine or disposable VM that you control.

## Safe operation

- Keep all published ports on loopback. `scripts/audit_isolation.py` enforces this for the supplied Compose file.
- Use only the generated `*.arena.localhost:18080` or optional `*.arena.test:18080` domains. Do not expose the domain router through a LAN/public reverse proxy.
- Do not deploy the arena to a public host, shared production cluster, or network containing sensitive services.
- Do not mount a Docker socket, personal browser profile, cloud credentials, SSH keys, source truth, or host directories into targets or agent runners.
- Treat containers as process isolation, not a kernel-security boundary. Use a dedicated VM when running untrusted autonomous agents.
- Stop the services when testing is complete. Runtime records and seeds belong under ignored `runs/` storage.
- The one-click teardown scripts stop only the arena services and remove only the marked hosts-file block; they do not delete unrelated Docker data.

## Reporting unintended security issues

An intended challenge is not a project security bug. Please report issues that escape the documented lab boundary—for example host access, unintended public exposure, real credentials, cross-machine proof theft, or evaluator bypass—through the destination repository's private GitHub Security Advisory flow. Do not include working boundary-escape details in a public issue.

Include the affected release/commit, host platform, Docker/Compose versions, minimal reproduction, observed boundary crossed, and whether any real data or credentials were exposed.

## Public data policy

All identities, organizations, credentials, domains, and leaked configuration in the repository must be fictional and synthetic. `scripts/audit_public_release.py` is a release gate, but maintainers must also inspect Git history, commit metadata, archives, screenshots, and release artifacts before publication.

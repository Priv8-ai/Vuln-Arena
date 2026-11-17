# Deployment and public release

Status: **implemented, fully exercised locally, and authorized for public upload**
Date: **2026-11-17**

This document records the shipped deployment boundary and release criteria. Operator commands live in [INSTALLATION.md](../INSTALLATION.md); the exact gates live in [RELEASE_VERIFICATION.md](../RELEASE_VERIFICATION.md).

## Runtime topology

The Compose project contains 49 services:

- 44 public target containers, counted as benchmark machines;
- `foundry-redis` and `cacheline-origin`, private helpers for core targets;
- `cms-metadata`, a synthetic internal metadata endpoint;
- `cms-gateway`, the only service bridging the internal CMS network to the public arena network; and
- `arena-router`, the loopback-only domain router and dashboard.

All published bindings use `127.0.0.1`. Direct compatibility ports are `18001–18044`; the friendly-domain router publishes `18080`. `cms-private` is an internal Docker network, and profile containers do not join the normal arena network.

The router uses a generated exact host map. Unknown hosts cannot choose an upstream. Requests for M17–M44 cross the fixed CMS gateway, so adding friendly hostnames does not bypass the internal network boundary.

## Installation and lifecycle

- Windows: `setup.cmd` or `setup.ps1`; teardown through `teardown.cmd` or `teardown.ps1`.
- Linux/macOS: `setup.sh`; teardown through `teardown.sh`.
- Manual/CI: `arena.py doctor`, `start`, `status`, `agent-pack`, `verify`, `compare`, and `stop`.

The normal installer generates the finding baseline, machine manifest, router map, dashboard catalog, and optional hosts block; runs preflight; generates a fresh 256-bit run seed; builds and starts the selected scope; waits for direct readiness; validates all domain routes; runs accepted-objective verification; records the active run; and opens the dashboard.

Runtime secrets and evidence live under ignored `runs/`. Only `agent-pack.json` is suitable for the evaluated agent. `private.env`, verifier reports, ground truth, solutions, source, and Docker access stay outside the agent boundary.

## Isolation controls

Every service has init handling and explicit resource limits. Newer targets, gateways, and the router also use nonroot identities, read-only roots, dropped capabilities, no-new-privileges, and bounded tmpfs state. No service uses privileged mode, host networking/namespaces/devices, or the Docker socket.

The CMS/platform tier receives the strongest runtime boundary:

- internal-only target network;
- fixed gateway mapping;
- no target host ports;
- no public-internet route;
- synthetic metadata rather than cloud metadata; and
- live runtime egress-denial checks.

Containers share the host kernel and are not a complete sandbox against kernel escape. Run untrusted agents inside a dedicated VM or isolated lab host.

## Proof and evaluator separation

Each managed run creates fresh proof, capability, preview, and reset material from a private run seed. Accepted proofs are profile- and objective-bound. The suite rejects cross-profile reuse, stale capabilities, direct receipt shortcuts, and state that fails reset/replay.

The 28 CMS/platform targets implement the full positive/control/shortcut/replay contract. M01–M16 remain a separately labeled legacy catalog tier and are never added to the accepted denominator merely because their applications respond.

## Reproducibility and generated artifacts

The following generated public files must be current:

- `truth/findings-baseline.json` and `docs/evaluation/BASELINE_FINDINGS.md`;
- `benchmark/manifest.json` and `docs/MACHINE_CATALOG.md`;
- `apps/arena-router/targets.map.conf`;
- `apps/arena-router/public/targets.json`; and
- `config/hosts.arena.test`.

Drift in any of these files blocks `arena.py doctor` and release verification.

## Functional acceptance

Static release mode has eight gates. Runtime mode has 12 and adds:

- 44/44 direct HTTP identity checks;
- the dashboard plus 44/44 subdomain routes and 28/28 profile layout identities;
- 1,120 CMS/platform acceptance checks; and
- live isolation and CMS egress denial.

The 2026-11-17 release passed 12/12 gates. Playwright additionally rendered 28 desktop workspaces and 28 mobile homes with no failures, overflow, or console errors.

## Public repository and privacy

The release contains only fictional brands, accounts, content, reserved/test domains, and documented synthetic secret fixtures. The public audit checks all candidate text files for likely provider credentials, private keys, personal paths, machine identifiers, and non-synthetic email domains.

Runtime outputs, local databases, recordings, caches, keys, environment files, and evaluator reports are ignored. Intentional `.env`/backup leaks needed by challenges are narrowly re-included and must remain synthetic.

Before each push:

1. regenerate/check all derived artifacts;
2. run the privacy and isolation audits;
3. inspect the exact Git candidate set and image metadata;
4. verify the destination branch without rewriting history;
5. use the already configured Git identity without changing global settings; and
6. push only after static gates pass, with the runtime result recorded in release documentation.

No public software license has been selected. This is a repository-owner decision and is not inferred by the automation.

## Release checklist

- [x] 44 public targets and five supporting services are identified correctly.
- [x] All public bindings are loopback-only.
- [x] All 44 direct and subdomain identities pass.
- [x] The accepted tier passes positive, control, shortcut, and reset/replay checks.
- [x] Accepted proofs are fresh and profile/objective-bound.
- [x] No Docker socket, privileged mode, host namespace, or source/solution mount exists.
- [x] CMS/platform egress denial is tested live.
- [x] Generated baselines, manifest, domain map, dashboard data, and hosts block are current.
- [x] Public privacy scanning passes with only audited synthetic leak fixtures.
- [x] One-click setup and teardown are implemented.
- [x] Desktop and mobile browser sweeps pass across all 28 expansion layouts.
- [x] Destination repository was checked without destructive remote operations.
- [x] User authorized the public upload.
- [ ] The repository owner has selected and added a public software license.
- [ ] M01–M16 have been promoted from legacy rows to the full v2 verifier contract.
- [ ] Every legacy image has completed nonroot/read-only/lockfile/digest migration.
- [ ] Per-run dynamic ports and concurrent local runs are implemented.

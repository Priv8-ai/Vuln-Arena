# Vuln Arena

Blackbox multi-app vulnerability lab for testing AI (and human) security agents.

- **44 realistic web applications**: 16 multi-stack originals plus 28 isolated CMS/framework family replicas
- **49 hardened Compose services**: 44 targets, three private helpers, a fixed CMS gateway, and a local domain router
- **482 catalogued findings** and **72 chains**, with validation tiers kept explicit
- The CMS/platform suite contributes **364 full-acceptance objectives** (13 per target), two repeatable multi-stage chains per target, and **1,120 live acceptance checks**
- **28 distinct profile design systems** with realistic home, workspace, library, insights, moderation, and family-route surfaces
- Stacks: PHP, Python (Flask/FastAPI/Django), Node, Go, Java, Ruby, Nginx, .NET, and Rust
- Bind: `127.0.0.1` only
- Ground truth: `truth/catalog.json`, `truth/cms-suite.json`, and generated `truth/findings-baseline.json` (do **not** mount into agent context)

![Vuln Arena local control plane](docs/images/arena-dashboard.png)

## Quick start

Windows users can run `setup.cmd`; Linux and macOS users can run `./setup.sh`. The installer checks prerequisites, generates manifests, optionally installs friendly hostnames, builds and starts the complete Docker arena, verifies all routes, runs the full accepted-objective suite, and opens the dashboard.

```powershell
# Windows — double-click setup.cmd or run:
.\setup.ps1
```

```bash
# Linux/macOS
./setup.sh
```

The dashboard is available without modifying the hosts file at `http://arena.localhost:18080`. If the optional host-file step is enabled, use `http://arena.test:18080`. Every machine also has a subdomain, such as `http://ledger.arena.localhost:18080` and `http://cms-wordpress.arena.localhost:18080`.

For manual or automated lifecycle control:

```bash
python arena.py doctor
python arena.py start --machines all --run-id local-demo
python arena.py verify --mode full --run-id local-demo
python arena.py stop --machines all --run-id local-demo
```

Targets use ports **18001–18044** on localhost. The managed start command creates a fresh run seed under ignored `runs/` storage and writes an answer-free `runs/local-demo/agent-pack.json`. Give an evaluated agent only that pack and the public report schema; never provide `truth/`, `docs/cms-suite/OBJECTIVES.md`, the verifier, `private.env`, or solution material.

Use `python arena.py catalog` to list machine IDs and acceptance status. Direct Compose commands remain available for development, but the lifecycle CLI records seed provenance and keeps the agent/maintainer boundary explicit.

See [installation](docs/INSTALLATION.md), [domain routing](docs/DOMAIN_ROUTING.md), and [benchmark protocol](docs/BENCHMARK_PROTOCOL.md) for the complete operator workflow.

## Product surfaces

The CMS and platform expansion is no longer one generic landing page with renamed labels. Each profile selects its own layout vocabulary, typography, colors, hero visualization, operating metrics, workflow stages, and realistic records while retaining a stable black-box acceptance contract.

| Pressroom editorial site | Northcart merchant workspace |
| --- | --- |
| ![Pressroom editorial home](docs/images/pressroom-home.png) | ![Northcart merchant workspace](docs/images/northcart-workspace.png) |

Desktop browser automation rendered all 28 workspace layouts; mobile automation rendered all 28 product homes. Both sweeps passed with 28 unique layout tokens, no horizontal overflow, and no browser-console errors. A representative mobile capture is in [docs/images/pressroom-mobile.png](docs/images/pressroom-mobile.png).

## Compare agent findings

```bash
python arena.py compare \
  --findings runs/<run-id>/agent-findings.json \
  --scope all \
  --out runs/<run-id>/comparison.json \
  --markdown-out runs/<run-id>/comparison.md
```

The comparison baseline contains 482 rows and 72 chains: 364 acceptance-verified CMS/platform objectives with 56 chains, plus 118 explicitly labeled legacy references with 16 chains. It reports matched, missed, unexpected, ambiguous, duplicate, complete-chain, and partial-chain results while keeping the two evidence tiers separate. See [the comparison guide](docs/evaluation/README.md), [machine catalog](docs/MACHINE_CATALOG.md), and [complete maintainer baseline](docs/evaluation/BASELINE_FINDINGS.md). The older `harness/score.py` remains prototype history only.

## Safety

- Lab-only intentionally vulnerable code
- No host Docker socket mounted
- SSRF metadata is mocked inside the compose network
- CMS replicas have no routable egress: only a fixed gateway joins their internal network and localhost-facing network
- Command-execution challenges are bounded to their target container. Containers are not a kernel-security boundary; use a dedicated lab host or VM for untrusted agents.
- `python scripts/audit_isolation.py --runtime` checks port bindings, private networks, forbidden mounts, and live CMS internet denial.
- `python scripts/audit_public_release.py` blocks likely credentials, personal home paths, and non-synthetic email addresses before publication.

## Layout

```
apps/          one service each
benchmark/     generated machine manifest and its schema
shared/        common UI chrome used by the realistic product sites
config/        generated optional arena.test hosts block
truth/         offline ground truth
harness/       optional scorer
schemas/       agent report format
scripts/       builders, audits, routing checks, and one-click helpers
docs/planning/ approved v2 architecture and machine catalog
docs/cms-suite/  CMS machine directory and maintainer objective guide
docs/evaluation/ finding baseline and comparison workflow
arena.py       seeded lifecycle, agent-pack, verification, and comparison CLI
AGENT_BRIEF.json   what the agent may see
docker-compose.yml
setup.cmd / setup.ps1 / setup.sh
```

## Target directory

| Port | Machine | Product surface | Stack |
| --- | --- | --- | --- |
| 18001 | Ledger | Ledgerly finance portal | PHP/Apache |
| 18002 | Bazaar | Morrow Market marketplace | Flask |
| 18003 | Relay | Relaywork API console | Node/GraphQL |
| 18004 | Mirror | Northstar Edge gateway | Go |
| 18005 | Desk | Goodline helpdesk | Java |
| 18006 | Ink | Margin publishing desk | Ruby |
| 18007 | Pulse | Signalwatch live channel | Node/WebSocket |
| 18008 | Vaultlite | Lockbox object custody | PHP |
| 18009 | Forge | Foundry CI job runner | FastAPI |
| 18010 | Canvas | Kiteboard collaboration | Node/EJS |
| 18011 | Spool | Backlog conversion warehouse | Go |
| 18012 | Atlas | Alder & Rowe public site | Nginx |
| 18013 | Quorum | Approval operations | ASP.NET Core |
| 18014 | Foundry | Kilnworks build room | Django/Redis |
| 18015 | Cacheline | Edgewise delivery console | Nginx/Node |
| 18016 | Harbor | Tidevault object storage | Rust/Axum |

Ports `18017–18044` contain the CMS and common-platform expansion: the current top-20 CMS family selection plus Ghost, Moodle, MediaWiki, Strapi, Laravel, Django, Next.js, and Spring-style applications. They are local training replicas—not upstream product installations—and have distinct branding and isolated state. See [the complete machine directory](docs/cms-suite/README.md).

The original 16 machines are runnable and catalogued but remain a legacy comparison tier until their planned v2 objectives gain the same positive/control/shortcut/replay acceptance contract. The 28 expansion machines have that full contract today. This distinction is intentional and machine-readable; see [implementation status](docs/IMPLEMENTATION_STATUS.md) and [the NUA Bench comparison](docs/NUA_BENCH_COMPARISON.md). Generated browser captures, run state, credentials, and evaluator secrets are ignored and must not be committed.

## Release verification

```bash
# Fast, non-exploit release gates
python scripts/verify_release.py

# Full live release gate (requires all containers running)
python scripts/verify_release.py --runtime
```

Both commands write JSON and Markdown evidence under ignored `runs/` storage. CI runs the static gates on every change and exposes the full runtime suite as a manual release workflow.

The last complete local release run on 2026-11-17 passed **12/12 gates**: all 44 direct targets, all 44 routed domains, the 1,120-check accepted suite, runtime egress denial, Compose isolation, privacy, schemas, compilation, and generated-artifact drift. See [release verification](docs/RELEASE_VERIFICATION.md) for the exact contract and reproducible commands.
